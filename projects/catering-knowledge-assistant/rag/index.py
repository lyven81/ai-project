"""
Stages 2 and 3 of the pipeline: embed and store.

Embeddings come from gemini-embedding-001, truncated to 768 dimensions via
Matryoshka representation learning and then L2 normalised. Only the full 3072
dimension output is pre-normalised by the API, so truncated vectors must be
normalised by hand or cosine similarity is distorted.

Storage is a real Qdrant collection running in local (embedded) mode, so there
is no server or container to manage. The collection carries payload indexes on
doc_type, category, authority and doc_id, which is what makes the filtered
searches in retriever.py run at the store level rather than in Python.
"""

import hashlib
import json
import time

import numpy as np
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, PayloadSchemaType,
)

from .config import (
    CHUNKS_JSON, QDRANT_PATH, COLLECTION, EMBED_MODEL, EMBED_DIM,
    EMBED_CACHE, load_api_key, qdrant_client,
)

# The free tier allows 100 embed requests per minute, and each content in a
# batch counts as one request. Pace below that ceiling and retry on 429.
BATCH = 20
RPM_LIMIT = 90
_request_times = []


def normalise(vectors):
    arr = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (arr / norms).tolist()


def _throttle(n):
    """Block until n more requests fit inside the rolling one minute window."""
    global _request_times
    while True:
        now = time.monotonic()
        _request_times = [t for t in _request_times if now - t < 60]
        if len(_request_times) + n <= RPM_LIMIT:
            return
        time.sleep(max(0.5, 60 - (now - _request_times[0]) + 0.5))


def _load_cache():
    if EMBED_CACHE.exists():
        return json.loads(EMBED_CACHE.read_text(encoding="utf-8"))
    return {}


def _key(text, task_type):
    raw = f"{EMBED_MODEL}|{EMBED_DIM}|{task_type}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _embed_batch(client, batch, task_type, attempt=0):
    try:
        _throttle(len(batch))
        _request_times.extend([time.monotonic()] * len(batch))
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBED_DIM,
            ),
        )
        return [e.values for e in resp.embeddings]
    except genai_errors.ClientError as e:
        if "RESOURCE_EXHAUSTED" not in str(e) or attempt >= 5:
            raise
        wait = min(60, 5 * (2 ** attempt))
        print(f"    rate limited, waiting {wait}s and retrying ...")
        time.sleep(wait)
        return _embed_batch(client, batch, task_type, attempt + 1)


def embed(client, texts, task_type, use_cache=True):
    """Embed texts with caching, batching, throttling and retry."""
    cache = _load_cache() if use_cache else {}
    keys = [_key(t, task_type) for t in texts]
    missing = [i for i, k in enumerate(keys) if k not in cache]

    if missing:
        print(f"  {len(texts) - len(missing)} cached, "
              f"{len(missing)} to embed")
        for start in range(0, len(missing), BATCH):
            idxs = missing[start:start + BATCH]
            vecs = _embed_batch(client, [texts[i] for i in idxs], task_type)
            for i, v in zip(idxs, vecs):
                cache[keys[i]] = v
            done = min(start + BATCH, len(missing))
            print(f"    {done}/{len(missing)}")
        if use_cache:
            EMBED_CACHE.write_text(json.dumps(cache), encoding="utf-8")

    return normalise([cache[k] for k in keys])


def embed_query(client, text):
    """A query is embedded with RETRIEVAL_QUERY, documents with RETRIEVAL_DOCUMENT.

    Using the matching task types is not cosmetic: the model places queries and
    documents in the same space only when told which is which.
    """
    return embed(client, [text], "RETRIEVAL_QUERY")[0]


def build():
    chunks = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
    client = genai.Client(api_key=load_api_key())

    print(f"Embedding {len(chunks)} chunks with {EMBED_MODEL} "
          f"at {EMBED_DIM} dimensions ...")
    vectors = embed(client, [c["text"] for c in chunks], "RETRIEVAL_DOCUMENT")

    qc, mode = qdrant_client()
    print(f"Qdrant mode: {mode}")
    if qc.collection_exists(COLLECTION):
        qc.delete_collection(COLLECTION)
    qc.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

    # Payload indexes accelerate filtered search on the server. In local mode
    # Qdrant filters correctly but ignores the index, so skip it quietly.
    if mode == "server":
        for field in ("doc_id", "doc_type", "category", "authority"):
            qc.create_payload_index(
                collection_name=COLLECTION,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )

    points = [
        PointStruct(id=i, vector=vectors[i], payload=chunks[i])
        for i in range(len(chunks))
    ]
    qc.upsert(collection_name=COLLECTION, points=points)

    info = qc.get_collection(COLLECTION)
    print(f"\nCollection '{COLLECTION}' built at {QDRANT_PATH.name}/")
    print(f"  points indexed   {info.points_count}")
    print(f"  vector size      {EMBED_DIM}")
    print(f"  distance         cosine")
    print(f"  payload indexes  {'doc_id, doc_type, category, authority' if mode == 'server' else 'skipped (local mode)'}")

    # Sanity check: a semantic query with no lexical overlap with its target.
    qv = embed_query(client, "which meals have no pork")
    hits = qc.query_points(COLLECTION, query=qv, limit=3).points
    print("\nSanity check, query: 'which meals have no pork'")
    for h in hits:
        print(f"  {h.score:.3f}  {h.payload['chunk_id']:<28} "
              f"{h.payload['heading'][:46]}")
    qc.close()


if __name__ == "__main__":
    build()
