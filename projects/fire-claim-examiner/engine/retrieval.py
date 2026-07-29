"""
Fire Claim Examiner: Layer 5, the retrieval stack.

Three stages, and the third is the one that matters:

    1. VECTOR      semantic search over clause-level embeddings (Qdrant)
    2. RERANK      cross-encoder scores each candidate against the query
    3. PRECEDENCE  candidates are re-ordered by LEGAL AUTHORITY

Stages 1 and 2 are ordinary RAG and any document assistant has them. Stage 3
is the reason this build exists. An insurance corpus contradicts itself by
design: an endorsement is written precisely to displace the base clause it sits
against. Similarity ranking returns Condition 6(b) ("Typhoon, hurricane... or
other atmospheric disturbance" excluded) and FP503 (storm covered) side by
side, both highly relevant, with no notion that one governs the other.

Authority is not a score to be blended. A held, engaged endorsement outranks
the exclusion it displaces however the cosine falls, so precedence is applied
as an ordering, not as a weight.
"""

import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import CrossEncoder, SentenceTransformer

BASE = next(c for c in (Path(__file__).resolve().parents[1],
                        Path(__file__).resolve().parents[2] / "app")
            if (c / "data").is_dir())
CHUNKS = BASE / "data" / "chunks.json"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
COLLECTION = "fire_policy"

# Lower number wins. An override is not "more relevant", it is superior.
AUTHORITY_RANK = {"override": 0, "primary": 1, "secondary": 2, "informational": 3}


class PolicyRetriever:
    def __init__(self, verbose=False):
        self.verbose = verbose
        data = json.loads(CHUNKS.read_text(encoding="utf-8"))
        self.chunks = data["chunks"]
        self.by_id = {c["chunk_id"]: c for c in self.chunks}

        self._log(f"loading {EMBED_MODEL}")
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self._log(f"loading {RERANK_MODEL}")
        self.reranker = CrossEncoder(RERANK_MODEL)

        # in-memory Qdrant: a real vector store, no server to run
        self.client = QdrantClient(":memory:")
        self._index()

    def _log(self, msg):
        if self.verbose:
            print(f"  [retriever] {msg}")

    def _index(self):
        texts = [f"{c['title']}\n{c['text']}" for c in self.chunks]
        self._log(f"embedding {len(texts)} chunks")
        vecs = self.embedder.encode(texts, batch_size=32, show_progress_bar=False)
        self.client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=vecs.shape[1], distance=Distance.COSINE),
        )
        self.client.upsert(COLLECTION, points=[
            PointStruct(id=i, vector=v.tolist(), payload={
                "chunk_id": c["chunk_id"], "code": c.get("code"),
                "type": c["type"], "authority": c["authority"],
                "peril": c.get("peril"), "overrides": c.get("overrides"),
                "title": c["title"],
            }) for i, (c, v) in enumerate(zip(self.chunks, vecs))
        ])
        self._log("indexed")

    # Words that place a query on a peril. Precedence only ever resolves
    # clauses competing on the SAME question, so the peril is what defines
    # which clauses are even in contention.
    PERIL_WORDS = {
        "flood": ("flood", "overflow", "river", "watercourse", "water mains",
                  "inundat", "sungai", "rose", "banks"),
        "storm": ("storm", "wind", "windstorm", "tempest", "gale", "cyclone",
                  "typhoon", "hurricane", "roof tiles", "gust"),
        "water_pipe": ("burst pipe", "burst water", "water pipe", "pipes",
                       "water tank", "apparatus", "plumbing", "leak"),
        "fire": ("fire", "burn", "blaze", "smoke", "ignit", "electrical fault"),
        "subsidence": ("subsidence", "landslip", "settle", "heave"),
        "earthquake": ("earthquake", "volcanic", "tremor"),
        "riot": ("riot", "strike", "malicious", "civil commotion"),
        "explosion": ("explosion", "explode", "boiler"),
        "impact": ("impact", "vehicle struck", "collision"),
        "falling_trees": ("tree", "branch", "falling tree"),
        "electrical": ("short circuit", "short-circuit", "arcing", "motor winding",
                       "over-running", "self heating"),
        "bush_fire": ("lalang", "bush fire", "undergrowth"),
    }

    def infer_peril(self, query: str):
        q = query.lower()
        best, hits = None, 0
        for peril, words in self.PERIL_WORDS.items():
            n = sum(w in q for w in words)
            if n > hits:
                best, hits = peril, n
        return best

    # ------------------------------------------------------------------ search
    def search(self, query: str, held: set | None = None, k: int = 8, pool: int = 25,
               peril: str | None = None):
        """Return candidates ordered by authority, then by rerank score.

        `held` is the customer's endorsement list. An endorsement that is not on
        the Schedule cannot override anything, so it is demoted out of the
        override tier rather than silently ranking first.
        """
        held = set(held or [])

        qv = self.embedder.encode(query).tolist()
        hits = self.client.query_points(COLLECTION, query=qv, limit=pool).points

        cands = []
        for h in hits:
            cid = h.payload["chunk_id"]
            c = self.by_id[cid]
            cands.append({"chunk_id": cid, "code": c.get("code"),
                          "title": c["title"], "type": c["type"],
                          "authority": c["authority"], "peril": c.get("peril"),
                          "overrides": c.get("overrides"),
                          "vector_score": float(h.score), "text": c["text"]})

        # stage 2: cross-encoder
        pairs = [(query, f"{c['title']} {c['text'][:1200]}") for c in cands]
        for c, s in zip(cands, self.reranker.predict(pairs)):
            c["rerank_score"] = float(s)

        # stage 3: precedence, applied ONLY among clauses in contention
        peril = peril or self.infer_peril(query)

        for c in cands:
            eff, note = c["authority"], ""

            # Is this clause even about the question asked? A clause tagged to
            # a different peril is not competing; promoting it on authority
            # ranked flood and earthquake above storm on a storm query.
            on_topic = (c["peril"] is None) or (peril is None) or (c["peril"] == peril)
            c["on_topic"] = on_topic

            if c["type"] == "coverage_decision":
                # Carries both the base position and the override plus the rule
                # for choosing between them, so it answers either way.
                note = (f"{c['code']} held: override applies" if c["code"] in held
                        else f"{c['code']} not held: {c['overrides']} stands")
            elif eff == "override" and c["code"] and c["code"] not in held:
                eff, note = "informational", "not held: cannot override"

            c["effective_authority"] = eff
            c["authority_note"] = note
            # off-topic clauses are ranked on relevance alone, never promoted
            c["authority_rank"] = AUTHORITY_RANK[eff] if on_topic else 9
            c["tier_bias"] = 0 if (on_topic and c["type"] == "coverage_decision") else 1

        cands.sort(key=lambda c: (not c["on_topic"], c["authority_rank"],
                                  c["tier_bias"], -c["rerank_score"]))
        return cands[:k]

    def explain(self, query: str, held=None, k=6):
        """Why the top result outranked the others. Feeds Under the Hood."""
        res = self.search(query, held, k=k)
        if not res:
            return {"query": query, "results": [], "winner": None}
        top = res[0]
        beaten = [r for r in res[1:]
                  if r["rerank_score"] > top["rerank_score"]]
        return {
            "query": query,
            "winner": top["chunk_id"],
            "results": res,
            "outranked_on_authority": [
                {"chunk_id": r["chunk_id"], "code": r["code"],
                 "rerank_score": round(r["rerank_score"], 3),
                 "authority": r["effective_authority"],
                 "why": f"scored higher on relevance ({r['rerank_score']:.2f} vs "
                        f"{top['rerank_score']:.2f}) but ranks below on authority"}
                for r in beaten],
        }


if __name__ == "__main__":
    r = PolicyRetriever(verbose=True)
    print()
    for q, held in [
        ("Does the policy cover flood damage?", {"FP504"}),
        ("Does the policy cover flood damage?", set()),
        ("burst water pipe while the shop lot was empty", {"FP507B"}),
        ("wind lifted roof tiles and rain came in through the gap", {"FP503"}),
    ]:
        print("=" * 74)
        print(f"Q: {q}    held: {sorted(held) or 'none'}")
        for c in r.search(q, held, k=4):
            print(f"   [{c['effective_authority']:13}] {c['chunk_id']:34} "
                  f"rr {c['rerank_score']:6.2f}  {c['authority_note']}")
