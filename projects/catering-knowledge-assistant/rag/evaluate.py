"""
Retrieval-quality and end-to-end evaluation.

Two passes, because they answer different questions and cost different amounts.

  retrieval  Is the right document reaching the generator at all? Cheap,
             repeatable, no generation calls. Also measures what the reranker
             is actually contributing, by scoring the same candidate set before
             and after the cross-encoder.

  end2end    Does the assistant route correctly, cite correctly, answer
             correctly, and refuse when it should? Costs one generation call
             per question.

Run:  python -m rag.evaluate retrieval
      python -m rag.evaluate end2end
      python -m rag.evaluate all
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from .retriever import search, rerank
from .config import TOP_K_VECTOR, TOP_K_RERANK

EVAL_SET = Path(__file__).parent / "eval_set.json"
RESULTS = Path(__file__).parent.parent / "eval_results.json"


def load_set():
    return json.loads(EVAL_SET.read_text(encoding="utf-8"))


def _pct(n, d):
    return f"{100.0 * n / d:5.1f}%" if d else "  n/a"


# ------------------------------------------------------------- retrieval ----

def eval_retrieval():
    cases = [c for c in load_set()
             if c["route"] == "corpus" and c.get("gold_docs")]
    rows = []

    for c in cases:
        gold = set(c["gold_docs"])
        cands = search(c["question"], k=TOP_K_VECTOR)
        # Three configurations scored on the same candidate pool, so the
        # comparison isolates what each stage contributes.
        plain = rerank(c["question"], list(cands), k=TOP_K_RERANK,
                       authority_aware=False)
        ranked = rerank(c["question"], list(cands), k=TOP_K_RERANK,
                        authority_aware=True)

        # Hit at k: did any gold document survive into the final context?
        vec_topk = cands[:TOP_K_RERANK]
        vec_hit = any(h.doc_id in gold for h in vec_topk)
        rr_hit = any(h.doc_id in gold for h in ranked)

        # Precision at k: proportion of the final context that is on target.
        vec_prec = sum(h.doc_id in gold for h in vec_topk) / max(1, len(vec_topk))
        rr_prec = sum(h.doc_id in gold for h in ranked) / max(1, len(ranked))

        # Reciprocal rank of the first gold document.
        def rr_of(hits):
            for i, h in enumerate(hits, 1):
                if h.doc_id in gold:
                    return 1.0 / i
            return 0.0

        # Recall over the wider candidate pool, the ceiling the reranker works within.
        recall_pool = any(h.doc_id in gold for h in cands)

        # Authority precedence: on questions where the FAQ restates an
        # authoritative document, does the authoritative one rank first?
        # Accepting either source hides whether precedence is respected, so
        # this is scored against a single required top document.
        top = set(c.get("top_doc", []))
        vec_top1 = (cands[0].doc_id in top) if (top and cands) else None
        pl_top1 = (plain[0].doc_id in top) if (top and plain) else None
        rr_top1 = (ranked[0].doc_id in top) if (top and ranked) else None

        # Counter-test. Authority precedence is meant to REORDER the context,
        # not empty it: the FAQ carries the plain-language phrasing that makes
        # an answer usable, so demoting it must not evict it. The originally
        # proposed counter-test (questions where the FAQ is the correct rank-1
        # source) has no instance in this corpus, because the FAQ restates a
        # policy on every question and is never a sole gold document. Retention
        # is the version of that test this corpus can actually support.
        faq_gold = "faq" in gold
        faq_retained = ("faq" in {h.doc_id for h in ranked}) if faq_gold else None

        rows.append({
            "id": c["id"], "tag": c["tag"], "question": c["question"],
            "gold": sorted(gold), "top_doc": sorted(top),
            "faq_gold": faq_gold, "faq_retained": faq_retained,
            "vector_hit": vec_hit, "rerank_hit": rr_hit,
            "vector_precision": vec_prec, "rerank_precision": rr_prec,
            "vector_mrr": rr_of(vec_topk), "rerank_mrr": rr_of(ranked),
            "plain_mrr": rr_of(plain),
            "plain_precision": sum(h.doc_id in gold for h in plain) / max(1, len(plain)),
            "plain_hit": any(h.doc_id in gold for h in plain),
            "recall_at_pool": recall_pool,
            "vector_top1_authority": vec_top1,
            "plain_top1_authority": pl_top1,
            "rerank_top1_authority": rr_top1,
            "vector_first": cands[0].doc_id if cands else "",
            "plain_first": plain[0].doc_id if plain else "",
            "rerank_first": ranked[0].doc_id if ranked else "",
            "final_docs": sorted({h.doc_id for h in ranked}),
        })

    n = len(rows)
    print(f"RETRIEVAL EVALUATION, {n} corpus questions")
    print(f"vector top-k = {TOP_K_VECTOR}, final context = {TOP_K_RERANK}\n")

    def avg(key):
        return sum(r[key] for r in rows) / n

    print(f"{'metric':<26}{'vector only':>13}{'+ reranker':>13}{'+ authority':>13}")
    print("-" * 65)
    print(f"{'hit rate at k':<26}"
          f"{_pct(sum(r['vector_hit'] for r in rows), n):>13}"
          f"{_pct(sum(r['plain_hit'] for r in rows), n):>13}"
          f"{_pct(sum(r['rerank_hit'] for r in rows), n):>13}")
    print(f"{'precision at k':<26}{avg('vector_precision'):>12.1%}"
          f"{avg('plain_precision'):>13.1%}{avg('rerank_precision'):>13.1%}")
    print(f"{'mean reciprocal rank':<26}{avg('vector_mrr'):>12.3f}"
          f"{avg('plain_mrr'):>13.3f}{avg('rerank_mrr'):>13.3f}")
    auth = [r for r in rows if r["top_doc"]]
    if auth:
        va = sum(bool(r["vector_top1_authority"]) for r in auth)
        pa = sum(bool(r["plain_top1_authority"]) for r in auth)
        ra = sum(bool(r["rerank_top1_authority"]) for r in auth)
        print(f"{'authority precedence @1':<26}{_pct(va, len(auth)):>13}"
              f"{_pct(pa, len(auth)):>13}{_pct(ra, len(auth)):>13}")
        print(f"{'':26}{'':>13}{'':>13}{f'n={len(auth)}':>13}")

    ret = [r for r in rows if r["faq_gold"]]
    if ret:
        kept = sum(bool(r["faq_retained"]) for r in ret)
        print(f"\ncounter-test, gold FAQ retained in context: "
              f"{_pct(kept, len(ret))}   ({kept}/{len(ret)})")
        print("  precedence must REORDER the context, not empty it. The FAQ")
        print("  carries the plain-language phrasing, so demoting it below the")
        print("  binding policy must not push it out of the final k.")
        for r in [x for x in ret if not x["faq_retained"]]:
            print(f"  evicted  {r['id']}  {r['question'][:56]}")

    print(f"\nrecall over the {TOP_K_VECTOR} candidate pool: "
          f"{_pct(sum(r['recall_at_pool'] for r in rows), n)}"
          f"   (the ceiling the reranker works within)")

    if auth:
        fixed = [r for r in auth if r["rerank_top1_authority"]
                 and not r["plain_top1_authority"]]
        broke = [r for r in auth if r["plain_top1_authority"]
                 and not r["rerank_top1_authority"]]
        print(f"\nauthority prior vs plain reranker: fixed {len(fixed)}, "
              f"broke {len(broke)}")
        for r in fixed[:8]:
            print(f"  fixed  {r['id']}  {r['question'][:48]}")
            print(f"         {r['plain_first']} -> {r['rerank_first']}")
        for r in broke[:8]:
            print(f"  broke  {r['id']}  {r['question'][:48]}")
            print(f"         {r['plain_first']} -> {r['rerank_first']}")
        print()
        still = [r for r in auth if not r["rerank_top1_authority"]]
        if still:
            print(f"authority precedence still wrong on {len(still)} of "
                  f"{len(auth)}:")
            for r in still:
                print(f"  {r['id']}  want {r['top_doc']}, got "
                      f"{r['rerank_first']}  |  {r['question'][:44]}")

    moved = [r for r in rows if r["rerank_mrr"] != r["vector_mrr"]]
    better = [r for r in moved if r["rerank_mrr"] > r["vector_mrr"]]
    worse = [r for r in moved if r["rerank_mrr"] < r["vector_mrr"]]
    print(f"\nreranker changed the top result on {len(moved)} of {n} questions: "
          f"{len(better)} improved, {len(worse)} regressed")
    for r in better[:6]:
        print(f"  improved  {r['id']}  {r['question'][:56]}")
    for r in worse[:6]:
        print(f"  regressed {r['id']}  {r['question'][:56]}")

    misses = [r for r in rows if not r["rerank_hit"]]
    if misses:
        print(f"\nmisses ({len(misses)}), no gold document in the final context:")
        for r in misses:
            print(f"  {r['id']} [{r['tag']}] {r['question']}")
            print(f"       gold: {r['gold']}")
            print(f"      given: {r['final_docs']}")

    by_tag = defaultdict(lambda: [0, 0])
    for r in rows:
        by_tag[r["tag"]][0] += int(r["rerank_hit"])
        by_tag[r["tag"]][1] += 1
    print("\nhit rate by question type:")
    for tag, (h, t) in sorted(by_tag.items(), key=lambda kv: kv[1][0] / kv[1][1]):
        print(f"  {tag:<26} {h}/{t}  {_pct(h, t)}")

    return rows


# ---------------------------------------------------------------- end2end ----

def eval_end2end():
    from .assistant import ask

    cases = load_set()

    # Resume. The free tier allows 20 generate_content calls per model per day
    # and each question costs two, so a full 48 question sweep cannot complete
    # in one day. Previously scored questions are carried forward and skipped,
    # so running this on consecutive days accumulates a complete set instead of
    # restarting at Q01 and burning the day's quota on the same first ten.
    rows, done = [], set()
    if RESULTS.exists():
        try:
            prev = json.loads(RESULTS.read_text(encoding="utf-8")).get("end2end")
        except ValueError:
            prev = None
        prev_rows = prev.get("rows", []) if isinstance(prev, dict) else (prev or [])
        ids = {c["id"] for c in cases}
        rows = [r for r in prev_rows if r.get("id") in ids]
        done = {r["id"] for r in rows}

    total = len(cases)
    todo = [c for c in cases if c["id"] not in done]
    print(f"END TO END EVALUATION, {total} questions")
    if done:
        print(f"resuming: {len(done)} already scored, {len(todo)} to go")
    print("(rate limited to the Gemini free tier, this takes a few minutes)\n")

    aborted = None
    for i, c in enumerate(todo, 1):
        # The free-tier daily cap can land mid-run. Losing 40 scored questions
        # because the 41st was throttled is worse than reporting a partial run,
        # so the sweep stops cleanly here and whatever was scored is kept and
        # labelled. Re-running later tops it up.
        try:
            a = ask(c["question"])
        except Exception as e:
            aborted = f"{type(e).__name__} at {c['id']} ({i}/{len(todo)}): {e}"
            print(f"\n  stopped early: {aborted}")
            break
        low = a.text.lower()

        route_ok = a.route == c["route"]
        tool_ok = (a.tool_name == c["tool"]) if c.get("tool") else None

        # Scored in BOTH directions. Guarding this on expect_refusal made
        # over-refusal invisible: an assistant that refused every question
        # scored 100% here, because the cases it got wrong were the ones the
        # check skipped. Refusing too much is as much a failure as refusing
        # too little, so every question is scored.
        expect_refusal = c.get("expect_refusal", False)
        refusal_ok = (a.refused == expect_refusal)

        want = [s.lower() for s in c.get("must_contain", [])]
        contains_ok = all(w in low for w in want) if want else None
        banned = [s.lower() for s in c.get("must_not_contain", [])]
        clean_ok = (not any(b in low for b in banned)) if banned else None

        gold = set(c.get("gold_docs", []))
        if c["route"] == "tool":
            cite_ok = a.citations == [f"database:{c['tool']}"] if c.get("tool") else None
        elif gold:
            cited_docs = {cc.split("#")[0].strip() for cc in a.citations}
            cite_ok = bool(cited_docs & gold) if a.citations else False
        else:
            cite_ok = None

        checks = [x for x in (route_ok, tool_ok, refusal_ok, contains_ok,
                              clean_ok, cite_ok) if x is not None]
        passed = all(checks)

        rows.append({
            "id": c["id"], "tag": c["tag"], "question": c["question"],
            "route_expected": c["route"], "route_actual": a.route,
            "tool_expected": c.get("tool", ""), "tool_actual": a.tool_name,
            "route_ok": route_ok, "tool_ok": tool_ok, "refusal_ok": refusal_ok,
            "refusal_expected": expect_refusal, "refused_actual": a.refused,
            "contains_ok": contains_ok, "clean_ok": clean_ok,
            "cite_ok": cite_ok, "passed": passed,
            "answer": a.text, "citations": a.citations,
        })
        flag = "pass" if passed else "FAIL"
        print(f"  [{i:2}/{len(todo)}] {c['id']} {flag}  {c['question'][:54]}")

    n = len(rows)
    if n < total:
        print(f"\nPARTIAL RUN: {n} of {total} questions scored. "
              f"Every figure below is over those {n} only.")
        print("Re-run `python -m rag.evaluate end2end` to resume and top up.")

    def rate(key):
        vals = [r[key] for r in rows if r[key] is not None]
        return sum(vals), len(vals)

    print(f"\n{'metric':<26}{'score':>12}{'rate':>10}")
    print("-" * 48)
    for label, key in [("route accuracy", "route_ok"),
                       ("tool selection", "tool_ok"),
                       ("citation accuracy", "cite_ok"),
                       ("answer correctness", "contains_ok"),
                       ("no forbidden content", "clean_ok"),
                       ("refusal correctness", "refusal_ok")]:
        p, t = rate(key)
        print(f"{label:<26}{f'{p}/{t}':>12}{_pct(p, t):>10}")
    p = sum(r["passed"] for r in rows)
    print(f"{'overall pass':<26}{f'{p}/{n}':>12}{_pct(p, n):>10}")

    # Refusal splits into two opposite failures, and they cost different
    # things: refusing an answerable question loses an order, answering an
    # unanswerable one gives a customer wrong information. Report them apart.
    over = [r for r in rows if r["refused_actual"] and not r["refusal_expected"]]
    under = [r for r in rows if r["refusal_expected"] and not r["refused_actual"]]
    print(f"\n{'refusal errors':<26}{'count':>12}")
    print("-" * 38)
    print(f"{'  over-refused (answerable)':<26}{len(over):>12}")
    print(f"{'  under-refused (unknown)':<26}{len(under):>12}")
    for r in over + under:
        kind = "over" if r in over else "under"
        print(f"  [{kind}] {r['id']} {r['question'][:52]}")

    fails = [r for r in rows if not r["passed"]]
    if fails:
        print(f"\nfailures ({len(fails)}):")
        for r in fails:
            reasons = [k.replace("_ok", "") for k in
                       ("route_ok", "tool_ok", "refusal_ok", "contains_ok",
                        "clean_ok", "cite_ok") if r[k] is False]
            print(f"  {r['id']} [{r['tag']}] {r['question']}")
            print(f"      failed: {', '.join(reasons)}")
            print(f"      answer: {r['answer'][:150]}")
            print(f"       cited: {r['citations']}")

    if n < total:
        # Recorded in the results file so a partial run can never be read as a
        # complete one, by a reader or by the frozen-bundle build.
        return {"partial": True, "scored": n, "of": total,
                "stopped_because": aborted, "rows": rows}
    return rows


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    mode = sys.argv[1] if len(sys.argv) > 1 else "retrieval"

    # Merge into whatever is already on disk rather than rebuilding. The two
    # halves cost very different things: retrieval is free and repeatable
    # (cached embeddings, local cross-encoder), while end to end spends two
    # generation calls per question and can be cut short by the free-tier quota.
    # Overwriting meant a solo run of either mode silently dropped the other.
    out = {}
    if RESULTS.exists():
        try:
            out = json.loads(RESULTS.read_text(encoding="utf-8"))
        except ValueError:
            out = {}

    if mode in ("retrieval", "all"):
        out["retrieval"] = eval_retrieval()
    if mode in ("end2end", "all"):
        if mode == "all":
            print("\n" + "=" * 62 + "\n")
        out["end2end"] = eval_end2end()
    RESULTS.write_text(json.dumps(out, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(f"\nresults written to {RESULTS.name}")


if __name__ == "__main__":
    main()
