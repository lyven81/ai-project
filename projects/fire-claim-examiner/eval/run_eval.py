"""
Fire Claim Examiner: Layer 3, the eval gate.

This runs BEFORE any UI exists and it is a hard gate. If it fails, the brain is
wrong and no screen gets built on top of it.

Gate:  determination 6/6  AND  payable 2/2 exact  AND  clause ranked first >= 5/6
"""

import json
import sys
from pathlib import Path

# Resolve the layout: this tree ships both inside the build folder (app/eval)
# and standalone in the portfolio (projects/{slug}/eval). Find the base that
# actually holds engine/ rather than assuming a fixed depth.
HERE = Path(__file__).resolve().parent
BASE = next(c for c in (HERE.parent, HERE.parents[1] / "app", HERE.parents[1])
            if (c / "engine").is_dir())
ROOT = BASE
sys.path.insert(0, str(BASE / "engine"))

from adjudicator import DeterministicFacts, adjudicate          # noqa: E402
from claim_parser import parse_all                              # noqa: E402

TRUTH = json.loads((BASE / "data" / "ground_truth.json").read_text("utf-8"))
BY_NO = {c["claim_no"]: c for c in TRUTH["claims"]}


def main():
    claims = parse_all(BASE / "claim case")
    extractor = DeterministicFacts()

    rows, det_ok, pay_ok, pay_total, first_ok, cite_ok, forbidden = [], 0, 0, 0, 0, 0, []

    for claim in claims:
        exp = BY_NO[claim["claim_no"]]
        got = adjudicate(claim, extractor.extract(claim))

        d_ok = got.verdict == exp["determination"]
        det_ok += d_ok

        p_ok = abs(got.payable - exp["payable"]) < 0.01
        if exp["determination"] == "APPROVE":
            pay_total += 1
            pay_ok += p_ok

        f_ok = got.governing_clause == exp["governing_clause"]
        first_ok += f_ok

        c_ok = bool(got.citations or got.grounds)
        cite_ok += c_ok

        for bad in exp.get("must_not_cite", []):
            if bad in got.citations:
                forbidden.append((claim["claim_no"], bad))

        rows.append({
            "claim": claim["claim_no"], "label": exp["label"],
            "exp_verdict": exp["determination"], "got_verdict": got.verdict,
            "verdict_ok": d_ok,
            "exp_pay": exp["payable"], "got_pay": got.payable, "pay_ok": p_ok,
            "exp_clause": exp["governing_clause"],
            "got_clause": got.governing_clause, "clause_ok": f_ok,
            "flags": got.flags,
        })

    n = len(claims)
    print("=" * 78)
    print("FIRE CLAIM EXAMINER  |  LAYER 3 EVAL GATE")
    print("=" * 78)
    print(f"{'CLAIM':16} {'VERDICT':22} {'PAYABLE':>22}  CLAUSE")
    print("-" * 78)
    for r in rows:
        v = f"{r['got_verdict']}/{r['exp_verdict']}"
        vm = "ok " if r["verdict_ok"] else "XX "
        pm = "ok " if r["pay_ok"] else "XX "
        cm = "ok" if r["clause_ok"] else "XX"
        pay = f"{r['got_pay']:,.0f}/{r['exp_pay']:,.0f}"
        print(f"{r['claim']:16} {vm}{v:19} {pm}{pay:>19}  {cm} {r['got_clause']}")
        if not r["clause_ok"]:
            print(f"{'':16}    expected clause: {r['exp_clause']}")

    print("-" * 78)
    print(f"axis 7  determination correct        {det_ok}/{n}")
    print(f"axis 8  payable exact to the ringgit {pay_ok}/{pay_total}")
    print(f"axis 2  governing clause ranked 1st  {first_ok}/{n}")
    print(f"axis 4  every answer cites a clause  {cite_ok}/{n}")
    if forbidden:
        print(f"axis 4  FORBIDDEN CITATIONS USED     {forbidden}")

    gate = (det_ok == n and pay_ok == pay_total and first_ok >= 5 and not forbidden)
    print("=" * 78)
    print("GATE PASSED. Layer 4 (UI) may proceed." if gate else
          "GATE FAILED. Fix the brain. Do not build UI on a wrong engine.")
    print("=" * 78)

    (BASE / "eval" / "results.json").write_text(
        json.dumps({"rows": rows, "gate_passed": gate,
                    "determination": f"{det_ok}/{n}",
                    "payable": f"{pay_ok}/{pay_total}",
                    "clause_first": f"{first_ok}/{n}"}, indent=2, default=str),
        encoding="utf-8")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
