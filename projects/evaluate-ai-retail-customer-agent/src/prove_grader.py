"""
THE HARD GATE. Mark the graders before trusting anything they say.

Runs the model graders over the 15 hand-written seeded answers, where every
fault is already known, and reports:

  catch rate        of the 10 planted faults, how many were flagged
  false-alarm rate  of the 5 clean controls, how many were wrongly flagged
  self-consistency  the same judge run twice on the same 15, how often it agrees
                    with itself
  judge agreement   how often the two providers reach the same verdict

Self-consistency is the number that decides whether a small V1-to-V2 gap can be
believed at all. A judge that disagrees with itself cannot resolve a difference
smaller than its own noise.

Gate: catch rate >= 0.80 and false-alarm rate <= 0.20 for at least one provider.
Below that, the graders get fixed before the experiment runs.

    python prove_grader.py                  both providers
    python prove_grader.py claude           one provider, when the other is down
"""

import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import pipeline

CATCH_MIN = 0.80
FALSE_ALARM_MAX = 0.20


def main():
    provs = [p for p in sys.argv[1:] if p in ("claude", "gemini")] or ["claude", "gemini"]
    keys = tuple("anthropic" if p == "claude" else "gemini" for p in provs)
    if not config.preflight(keys):
        print("Aborting: a provider is unavailable."
              " Nothing was run, nothing was overwritten.")
        return 2

    seeded = config.load_json("seeded-answers.json")["seeded"]
    cases = {c["id"]: c for c in config.load_json("dataset.json")["cases"]}

    jobs = []
    for s in seeded:
        for p in provs:
            jobs.append((s, p, "run1"))
        # Self-consistency probe on the first provider only: one repeat is
        # enough to show whether the instrument is stable, and a second costs
        # as much as the whole first pass.
        jobs.append((s, provs[0], "run2"))

    def work(job):
        s, provider, run = job
        return (s["id"], provider, run,
                pipeline.model_grade(s["response"], s["question"], provider))

    print(f"Grading {len(seeded)} seeded answers with {', '.join(provs)}"
          f", {len(jobs)} calls...")
    with ThreadPoolExecutor(max_workers=6) as ex:
        out = list(ex.map(work, jobs))

    graded = {}
    for sid, provider, run, g in out:
        graded.setdefault(sid, {})[f"{provider}_{run}"] = g

    rows = []
    for s in seeded:
        g = graded[s["id"]]
        row = {"id": s["id"], "case_id": s["case_id"],
               "fault_type": s["truth"]["fault_type"],
               "truth_has_violation": s["truth"]["has_violation"],
               "code_grade": pipeline.code_grade(s["response"], cases[s["case_id"]])}
        for p in provs:
            row[p] = g[f"{p}_run1"]
        row["repeat"] = g[f"{provs[0]}_run2"]
        rows.append(row)

    def rate(provider, want_truth):
        """Only rows where the grader actually returned a verdict.

        A call that errored has no verdict. Counting it as 'did not flag' would
        charge a rate limit to the judge's accuracy, so it is excluded from the
        denominator and reported separately as an error.
        """
        sub = [r for r in rows if r["truth_has_violation"] is want_truth
               and r[provider].get("has_violation") is not None]
        return len([r for r in sub if r[provider]["has_violation"] is True]), len(sub)

    summary = {"policy_hash": config.policy_hash(), "providers": provs,
               "grader_claude": config.GRADER_CLAUDE if "claude" in provs else None,
               "grader_gemini": config.GRADER_GEMINI if "gemini" in provs else None,
               "n_seeded": len(rows)}

    print("\n" + "=" * 70)
    for p in provs:
        tp, nf = rate(p, True)
        fp, nc = rate(p, False)
        catch = tp / nf if nf else 0
        fa = fp / nc if nc else 0
        errs = sum(1 for r in rows if r[p].get("has_violation") is None)
        summary[p] = {"catch_rate": round(catch, 3), "caught": tp, "of_faulty": nf,
                      "false_alarm_rate": round(fa, 3), "false_alarms": fp, "of_clean": nc,
                      "no_verdict_errors": errs,
                      "passes_gate": nf > 0 and catch >= CATCH_MIN and fa <= FALSE_ALARM_MAX}
        print(f"{p:8s} catch {tp}/{nf} = {catch:.0%}   false alarm {fp}/{nc} = {fa:.0%}"
              f"   errors {errs}   {'PASS' if summary[p]['passes_gate'] else 'FAIL'}")

    pair = [r for r in rows if r[provs[0]].get("has_violation") is not None
            and r["repeat"].get("has_violation") is not None]
    selfc = sum(1 for r in pair
                if r[provs[0]]["has_violation"] == r["repeat"]["has_violation"])
    summary["self_consistency"] = {"provider": provs[0], "agree": selfc, "of": len(pair),
                                   "rate": round(selfc / len(pair), 3) if pair else None}
    print(f"\n{provs[0]} self-consistency  {selfc}/{len(pair)}"
          + (f" = {selfc/len(pair):.0%}" if pair else " (n/a)"))

    if len(provs) > 1:
        both = [r for r in rows if all(r[p].get("has_violation") is not None for p in provs)]
        agree = sum(1 for r in both
                    if r[provs[0]]["has_violation"] == r[provs[1]]["has_violation"])
        summary["judge_agreement"] = {"agree": agree, "of": len(both),
                                      "rate": round(agree / len(both), 3) if both else None}
        print(f"judge agreement      {agree}/{len(both)}"
              + (f" = {agree/len(both):.0%}" if both else " (n/a)"))

    p0 = provs[0]
    misses = [(r["id"], r["fault_type"]) for r in rows
              if r["truth_has_violation"] and r[p0].get("has_violation") is False]
    fps = [r["id"] for r in rows
           if not r["truth_has_violation"] and r[p0].get("has_violation") is True]
    noverdict = [r["id"] for r in rows if r[p0].get("has_violation") is None]
    if misses:
        print(f"\n{p0} MISSED: {misses}")
    if fps:
        print(f"{p0} FALSE ALARM on: {fps}")
    if noverdict:
        print(f"{p0} NO VERDICT (call failed, not a judgement): {noverdict}")

    cg = [r for r in rows if r["code_grade"]]
    cg_correct = [r for r in cg if (not r["code_grade"]["passed"]) == r["truth_has_violation"]]
    cg_blind = [r["id"] for r in cg if r["code_grade"]["passed"] and r["truth_has_violation"]]
    summary["code_grader"] = {"cases_with_assertions": len(cg),
                              "verdict_matches_truth": len(cg_correct),
                              "blind_to_fault_on": cg_blind}
    print(f"\ncode grader: {len(cg_correct)}/{len(cg)} verdicts match the known truth")
    if cg_blind:
        print(f"  blind to the fault on {cg_blind}"
              f" (all assertions pass, the fault is not a wrong value)")

    summary["passes_gate"] = any(summary[p]["passes_gate"] for p in provs)
    print("\n" + "=" * 70)
    print("GATE:", "PASS" if summary["passes_gate"] else "FAIL")

    config.archive_existing("grader_proof.json")
    io.open(config.RESULTS / "grader_proof.json", "w", encoding="utf-8").write(
        json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False))
    print("written -> results/grader_proof.json")
    return 0 if summary["passes_gate"] else 1


if __name__ == "__main__":
    sys.exit(main())
