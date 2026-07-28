"""Sweep RELEVANCE_FLOOR (python -m rag.sweep_floor), the one tunable in the authority precedence rule.

Cross-encoder scores do not depend on the floor, so every pool is scored once
and only the ordering is recomputed per floor.
"""
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from rag import retriever as R
from rag.config import TOP_K_VECTOR, TOP_K_RERANK

cases = [c for c in json.load(open("rag/eval_set.json", encoding="utf-8"))
         if c["route"] == "corpus" and c.get("gold_docs")]
auth = [c for c in cases if c.get("top_doc")]
print(f"{len(cases)} corpus questions, {len(auth)} authority-tagged\n", flush=True)

def scored(query, hits):
    s = R._cross_encoder().predict([(query, h.text) for h in hits])
    for h, v in zip(hits, s):
        h.rerank_score = float(v); h.final_score = float(v)
    return hits

pools, parents = {}, {}
for i, c in enumerate(cases, 1):
    pools[c["id"]] = scored(c["question"], R.search(c["question"], k=TOP_K_VECTOR))
    # Pre-resolve any binding parent that is missing from the pool.
    have = {h.doc_id for h in pools[c["id"]]}
    for h in pools[c["id"]]:
        if h.restates and h.restates not in have:
            key = (c["id"], h.restates)
            if key not in parents:
                parents[key] = R._fetch_parent(c["question"], h.restates)
    print(f"  scored {i}/{len(cases)}", end="\r", flush=True)
print(" " * 40, end="\r")

def rank(c, floor):
    R.RELEVANCE_FLOOR = floor
    pool = pools[c["id"]]
    ranked = sorted(pool, key=lambda h: R._rank_key(h, True))
    pool_plus = list(pool) + [p for (cid, _), p in parents.items()
                              if cid == c["id"] and p is not None]
    return R._promote_binding_parents(c["question"], ranked, pool_plus,
                                      fetch_missing=False)[:TOP_K_RERANK]

print(f"{'floor':>7}{'precedence@1':>15}{'precision@4':>14}{'hit@4':>9}{'fails':>7}")
print("-" * 52)
rows = []
for floor in [-12.0, -8.0, -6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0]:
    prec, hits, ok, fails = [], [], 0, []
    for c in cases:
        ranked = rank(c, floor)
        gold = set(c["gold_docs"])
        prec.append(sum(h.doc_id in gold for h in ranked) / max(1, len(ranked)))
        hits.append(any(h.doc_id in gold for h in ranked))
        top = set(c.get("top_doc", []))
        if top:
            if ranked and ranked[0].doc_id in top: ok += 1
            else: fails.append((c["id"], ",".join(sorted(top)),
                                ranked[0].doc_id if ranked else "-", c["question"]))
    rows.append((floor, ok/len(auth), sum(prec)/len(prec), sum(hits)/len(hits), fails))
    print(f"{floor:>7.1f}{ok/len(auth):>14.1%}{sum(prec)/len(prec):>14.1%}"
          f"{sum(hits)/len(hits):>9.1%}{len(fails):>7}", flush=True)

best = max(rows, key=lambda r: (r[1], r[2]))
print(f"\nbest: floor {best[0]}  precedence {best[1]:.1%}  precision {best[2]:.1%}")
if best[4]:
    print("remaining failures:")
    for i, want, got, q in best[4]:
        print(f"  {i}  want {want:<24} got {got:<24} {q[:46]}")
