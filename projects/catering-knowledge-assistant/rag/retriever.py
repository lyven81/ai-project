"""
Stages 4 and 5 of the pipeline: retrieve and rerank.

Two stages, on purpose. Vector search is fast and recall-oriented but it scores
a query against a whole chunk embedding, so it confuses documents that talk
about the same subject in different roles. This corpus is built to expose that:
the FAQ restates the policies, so a question about pausing a subscription pulls
both the FAQ answer and the refund policy with near identical similarity.

The cross-encoder reads the query and the candidate together rather than
comparing two independent embeddings, so it can tell which one actually answers
the question. It runs locally on CPU at no API cost.
"""

from dataclasses import dataclass

from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

from .config import (
    COLLECTION, RERANK_MODEL, TOP_K_VECTOR, TOP_K_RERANK, MIN_RERANK_SCORE,
    RELEVANCE_FLOOR, qdrant_client, load_api_key,
)

_encoder = None
_gemini = None
_qc = None
_mode = None


def _cross_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import CrossEncoder
        _encoder = CrossEncoder(RERANK_MODEL)
    return _encoder


def _client():
    global _gemini
    if _gemini is None:
        from google import genai
        _gemini = genai.Client(api_key=load_api_key())
    return _gemini


def _store():
    global _qc, _mode
    if _qc is None:
        import atexit
        _qc, _mode = qdrant_client()
        # Close explicitly, otherwise the client's __del__ runs during
        # interpreter shutdown and raises a confusing ImportError.
        atexit.register(lambda: _qc.close())
    return _qc


def store_mode():
    _store()
    return _mode


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    doc_type: str
    authority: str
    heading: str
    text: str
    vector_score: float
    rerank_score: float = 0.0   # raw cross-encoder score
    final_score: float = 0.0    # cross-encoder score plus the authority prior
    restates: str = ""          # binding doc_id this chunk restates, if any
    promoted: bool = False      # pulled up as the binding parent of a hit


def build_filter(doc_types=None, categories=None, authorities=None, doc_ids=None):
    """Compose a Qdrant payload filter. Returns None when nothing is constrained."""
    must = []
    for field, values in (("doc_type", doc_types), ("category", categories),
                          ("authority", authorities), ("doc_id", doc_ids)):
        if not values:
            continue
        if isinstance(values, str):
            must.append(FieldCondition(key=field, match=MatchValue(value=values)))
        else:
            must.append(FieldCondition(key=field, match=MatchAny(any=list(values))))
    return Filter(must=must) if must else None


_qvec_memo = {}


def _query_vector(query):
    """Embed a query once per process.

    embed() is cached on disk, but that cache is a 1.8 MB JSON file reloaded on
    every call. A parent fetch re-searches with the same query, so memoising in
    process keeps that second lookup free.
    """
    if query not in _qvec_memo:
        from .index import embed
        _qvec_memo[query] = embed(_client(), [query], "RETRIEVAL_QUERY")[0]
    return _qvec_memo[query]


def search(query, k=TOP_K_VECTOR, qfilter=None):
    """Stage 4: dense vector search with an optional payload filter."""
    qv = _query_vector(query)
    res = _store().query_points(
        collection_name=COLLECTION,
        query=qv,
        limit=k,
        query_filter=qfilter,
        with_payload=True,
    ).points
    return [Hit(
        chunk_id=p.payload["chunk_id"],
        doc_id=p.payload["doc_id"],
        doc_type=p.payload["doc_type"],
        authority=p.payload["authority"],
        heading=p.payload["heading"],
        text=p.payload["text"],
        vector_score=p.score,
        restates=p.payload.get("restates", "") or "",
    ) for p in res]


# Authority precedence.
#
# Measured problem: FAQ chunks are short and question-shaped, so they match
# query phrasing closely and take the top slot from the document that actually
# binds. On the labelled set that put authority precedence at 13%. The FAQ is
# tagged secondary precisely because it restates the policies and can drift
# from them, so grounding an answer on it is a real correctness risk.
#
# The first design added a constant to the cross-encoder score. That cannot
# reach 100% by construction: the scores are unbounded (roughly -11 to +10, so
# margins reach about 21) and a fixed bonus loses to any larger margin. The
# sweep is asymptotic, which is the signature of the wrong mechanism:
#
#   bonus (primary/override)   authority@1   precision@4   hit rate@4
#   0  / 0                          13.0%         90.5%         100%
#   4  / 6                          43.5%         82.4%         100%
#   8  / 12                         69.6%         77.7%         100%
#   12 / 18                         82.6%         73.6%         100%
#
# So authority is now applied as an ordering rule rather than a score. Among
# chunks that clear RELEVANCE_FLOOR, order is authority first and score second;
# below the floor, score alone. That makes precedence unconditional wherever a
# binding chunk is genuinely relevant, without the failure mode of filtering:
# nothing is discarded, so a question the override does not cover (asking about
# 3 September when the notice only covers two other dates) still has the
# standing policy in context.
#
# The floor replaces both bonus constants with one interpretable number: how
# relevant a binding document must be before it may outrank a better-matching
# restatement. Unlike the bonus sweep it has a real optimum, because the two
# failure modes sit on opposite sides. Too low and a weakly-matching override
# outranks the policy that actually answers ("When must I place my order?" was
# lost to the holiday notice at +1.10). Too high and the rule stops firing.
#
#   floor   precedence@1   precision@4   hit@4
#   -12.0        65.2%         67.6%      100%
#    -8.0        87.0%         82.4%      100%
#    -6.0        91.3%         83.8%      100%
#     0.0        91.3%         85.1%      100%
#     2.0       100.0%         87.2%      100%   <- operating point
#     4.0        95.7%         87.8%      100%
#     8.0        95.7%         87.8%      100%
#
# Precision rises rather than falls, unlike under the additive prior, because
# ordering by authority no longer costs the gold FAQ its place in the context.
# Caveat: 100% is reached at a single swept value with 95.7% on either side, on
# 23 labelled questions, so treat the exact floor as fitted to this set. The
# shape of the curve is the durable result, not the decimal.
AUTHORITY_RANK = {"override": 0, "primary": 1, "secondary": 2}


def _rank_key(h, authority_aware):
    """Sort key. Lower is better, matching AUTHORITY_RANK."""
    if authority_aware and h.rerank_score >= RELEVANCE_FLOOR:
        return (0, AUTHORITY_RANK.get(h.authority, 3), -h.rerank_score)
    # Not relevant enough to claim precedence, so rank on similarity alone.
    return (1, 0, -h.rerank_score)


def _fetch_parent(query, doc_id):
    """Pull the best chunk of a named binding document into the pool.

    A restatement can outrank its parent so decisively that the parent never
    reaches the candidate pool at all ("Is there a weekly plan?" retrieves three
    FAQ chunks and no subscription_guide). The pointer names the document, so
    fetch it directly rather than hoping similarity surfaces it.
    """
    hits = search(query, k=3, qfilter=build_filter(doc_ids=doc_id))
    if not hits:
        return None
    scores = _cross_encoder().predict([(query, h.text) for h in hits])
    for h, s in zip(hits, scores):
        h.rerank_score = float(s)
        h.final_score = h.rerank_score
    return max(hits, key=lambda h: h.rerank_score)


def _promote_binding_parents(query, ranked, pool, fetch_missing=True):
    """Pull a secondary chunk's binding parent in above it.

    A secondary chunk that names its parent ("See delivery_policy.") is a
    restatement. Whenever one appears, the parent is placed directly above it so
    the binding text is in context and is cited first. Chunks with no pointer
    are FAQ-only facts with no binding parent, and are left alone.
    """
    best_in_pool = {}
    for h in pool:
        prev = best_in_pool.get(h.doc_id)
        if prev is None or h.rerank_score > prev.rerank_score:
            best_in_pool[h.doc_id] = h

    out, placed, placed_docs = [], set(), set()

    def add(hit):
        if hit.chunk_id not in placed:
            placed.add(hit.chunk_id)
            placed_docs.add(hit.doc_id)
            out.append(hit)

    for h in ranked:
        if h.restates and h.restates not in placed_docs:
            parent = best_in_pool.get(h.restates)
            if parent is None and fetch_missing:
                parent = _fetch_parent(query, h.restates)
            if parent is not None and parent.chunk_id != h.chunk_id:
                parent.promoted = True
                add(parent)
        add(h)
    return out


def rerank(query, hits, k=TOP_K_RERANK, authority_aware=True,
           fetch_missing=True):
    """Stage 5: cross-encoder rerank, apply authority precedence, cut to k."""
    if not hits:
        return []
    pairs = [(query, h.text) for h in hits]
    scores = _cross_encoder().predict(pairs)
    for h, s in zip(hits, scores):
        h.rerank_score = float(s)
        h.final_score = h.rerank_score

    ranked = sorted(hits, key=lambda h: _rank_key(h, authority_aware))
    if authority_aware:
        ranked = _promote_binding_parents(query, ranked, hits,
                                          fetch_missing=fetch_missing)
    return ranked[:k]


def retrieve(query, k_vector=TOP_K_VECTOR, k_final=TOP_K_RERANK, qfilter=None):
    """Full retrieval: search, rerank, drop anything below the relevance floor."""
    candidates = search(query, k=k_vector, qfilter=qfilter)
    ranked = rerank(query, candidates, k=k_final)
    return [h for h in ranked if h.rerank_score >= MIN_RERANK_SCORE]


def demo():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(f"Qdrant mode: {store_mode()}\n")

    queries = [
        ("can I pause my subscription", None),
        ("do you deliver on 31 August", None),
        ("do you deliver on 31 August", build_filter(authorities="override")),
        ("what is the claypot chicken price", None),
    ]
    for q, f in queries:
        label = " [filter: authority=override]" if f else ""
        print(f"QUERY: {q}{label}")
        cands = search(q, qfilter=f)
        ranked = rerank(q, cands)
        print(f"  vector stage, top 4 of {len(cands)}:")
        for h in cands[:4]:
            print(f"    {h.vector_score:.3f}  {h.chunk_id:<30} [{h.authority}]")
        print("  after cross-encoder rerank:")
        for h in ranked:
            print(f"    {h.rerank_score:+.2f}  {h.chunk_id:<30} [{h.authority}]")
        print()


if __name__ == "__main__":
    demo()
