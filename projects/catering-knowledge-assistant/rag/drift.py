"""Drift test: does the binding document still win when the FAQ goes stale?

Authority precedence is measured as a ranking statistic (does the binding
document reach rank 1). That only matters if a wrong ranking produces a wrong
answer, and on the clean corpus it usually does not, because the FAQ and the
policy agree. So the ranking metric cannot show what the feature is worth.

This test creates the disagreement on purpose. It takes FAQ entries that restate
a policy and rewrites them to contradict it (the cut-off moves to 9:00pm, the
refund policy flips, a third delivery area appears), then asks the matching
question and checks which document the retrieval follows.

The drifted text is never written to corpus/. It is embedded and upserted into a
SEPARATE Qdrant collection built for the run and dropped afterwards, so the
shipped corpus and its hash stay clean.

    python -m rag.drift              # run against the current ranking rule
    python -m rag.drift --baseline   # also run with authority disabled
"""

import json
import sys

from qdrant_client.models import Distance, VectorParams, PointStruct

from .config import (
    COLLECTION, CHUNKS_JSON, EMBED_DIM, TOP_K_VECTOR, TOP_K_RERANK,
    load_api_key,
)
from . import retriever as R

DRIFT_SET = __file__.replace("drift.py", "drift_set.json")
DRIFT_COLLECTION = COLLECTION + "_drift"


def load_drift():
    with open(DRIFT_SET, encoding="utf-8") as f:
        return json.load(f)


def build_drift_collection(cases):
    """Clone the corpus with the drifted FAQ chunks swapped in."""
    from google import genai
    from .index import embed

    chunks = json.loads(open(CHUNKS_JSON, encoding="utf-8").read())
    by_id = {c["chunk_id"]: c for c in chunks}

    changed = []
    for case in cases:
        c = by_id.get(case["chunk_id"])
        if c is None:
            raise LookupError(f"{case['chunk_id']} not in chunks.json")
        if case["find"] not in c["text"]:
            raise ValueError(
                f"{case['id']}: drift anchor not found in {case['chunk_id']}. "
                "The corpus changed; update drift_set.json.")
        c = dict(c)
        c["text"] = c["text"].replace(case["find"], case["replace"])
        by_id[case["chunk_id"]] = c
        changed.append(c)

    corpus = list(by_id.values())
    client = genai.Client(api_key=load_api_key())
    # Only the drifted chunks are new; everything else is served from the cache.
    vectors = embed(client, [c["text"] for c in corpus], "RETRIEVAL_DOCUMENT")

    # Reuse the retriever's client. Local Qdrant permits one client per storage
    # folder, so opening a second here deadlocks against the one search() uses.
    qc = R._store()
    if qc.collection_exists(DRIFT_COLLECTION):
        qc.delete_collection(DRIFT_COLLECTION)
    qc.create_collection(
        DRIFT_COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE))
    qc.upsert(DRIFT_COLLECTION, points=[
        PointStruct(id=i, vector=vectors[i], payload=corpus[i])
        for i in range(len(corpus))])
    return qc, len(changed)


def run(authority_aware=True):
    cases = load_drift()
    qc, n_changed = build_drift_collection(cases)

    # Point the retriever at the drifted collection for the duration.
    original = R.COLLECTION
    R.COLLECTION = DRIFT_COLLECTION
    rows = []
    try:
        for case in cases:
            hits = R.search(case["question"], k=TOP_K_VECTOR)
            ranked = R.rerank(case["question"], hits, k=TOP_K_RERANK,
                              authority_aware=authority_aware)
            top = ranked[0] if ranked else None
            docs = [h.doc_id for h in ranked]
            rows.append({
                "id": case["id"],
                "question": case["question"],
                "binding_doc": case["binding_doc"],
                "top_doc": top.doc_id if top else "-",
                "follows_binding": bool(top and top.doc_id == case["binding_doc"]),
                "binding_in_context": case["binding_doc"] in docs,
                "context": docs,
                "binding_fact": case["binding_fact"],
                "stale_fact": case["stale_fact"],
            })
    finally:
        R.COLLECTION = original
        qc.delete_collection(DRIFT_COLLECTION)
    return rows, n_changed


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    baseline = "--baseline" in sys.argv
    modes = [("authority precedence", True)]
    if baseline:
        modes.insert(0, ("no authority rule", False))

    for label, aware in modes:
        rows, n = run(authority_aware=aware)
        follow = sum(r["follows_binding"] for r in rows)
        inctx = sum(r["binding_in_context"] for r in rows)
        print(f"\nDRIFT TEST, {label}")
        print(f"{n} FAQ entries rewritten to contradict the policy they restate\n")
        print(f"{'id':<5}{'question':<34}{'top document':<26}{'follows policy':>15}")
        print("-" * 80)
        for r in rows:
            print(f"{r['id']:<5}{r['question'][:32]:<34}{r['top_doc']:<26}"
                  f"{'yes' if r['follows_binding'] else 'NO':>15}")
        print("-" * 80)
        print(f"{'binding document ranked first':<44}{follow}/{len(rows)}")
        print(f"{'binding document present in context':<44}{inctx}/{len(rows)}")
        for r in rows:
            if not r["follows_binding"]:
                print(f"\n  {r['id']} would answer from the stale FAQ: "
                      f"\"{r['stale_fact']}\" instead of \"{r['binding_fact']}\"")


if __name__ == "__main__":
    main()
