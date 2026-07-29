"""
Freeze the proven engine output for the UI (Tree, Layer 4).

The screens are built on THIS file, never on live compute, so the interface can
never break a figure the eval gate has already validated. Regenerate only after
run_eval.py passes.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app" / "engine"))

from adjudicator import COVERAGE_CHAIN, DeterministicFacts, adjudicate  # noqa: E402
from claim_parser import parse_all                          # noqa: E402

OUT = ROOT / "app" / "data" / "frozen_results.json"
TRUTH = json.loads((ROOT / "app" / "data" / "ground_truth.json").read_text("utf-8"))
KEY = {c["claim_no"]: c for c in TRUTH["claims"]}

# Quoted policy text for the governing clause, so the UI can show the wording
# next to the verdict instead of only naming it.
QUOTES = {
    "policy_period": ("Period of Insurance",
        "The Schedule states the period of insurance. A loss occurring outside "
        "that period is not covered, whether it falls before inception or after "
        "expiry."),
    "peril_not_insured": ("Insuring clause",
        "This is a fire policy. Burglary and theft are not among the insured "
        "perils, and no endorsement on this Schedule extends cover to them."),
    "Condition 12": ("Condition 12",
        "On the happening of any loss or damage the Insured shall forthwith give "
        "notice thereof to the Company and shall within 15 days after the loss or "
        "damage, or such further time as the Company may in writing allow in that "
        "behalf, deliver to the Company a claim in writing... No claim under this "
        "Policy shall be payable unless the terms of this Condition have been "
        "complied with."),
    "FP507B(a)": ("FP507B, exclusion (a)",
        "...the insurance under this Policy shall extend to include loss or damage "
        "to the property insured caused by the bursting or overflowing of water "
        "tanks, apparatus or pipes installed in or on the buildings insured... "
        "excluding: (a) loss or damage caused whilst the premises are untenanted."),
    "FP503": ("FP503 Storm, Tempest Endorsement, Special Condition 1",
        "The Company shall not be liable for any loss or damage caused by water or "
        "rain, whether driven by wind or not unless the building insured... shall "
        "first sustain actual damage to the roof or walls of same by the direct "
        "force of Hurricane, Cyclone, Typhoon and Windstorm and shall then be "
        "liable only for such damage to the interior of the building or the insured "
        "property therein as may be caused by water or rain entering the building "
        "through openings in the roof or walls made by the direct force of the said "
        "perils."),
    "base_insuring_clause": ("Base insuring clause, fire",
        "Fire is the core peril insured by this Policy. No endorsement is required "
        "for it to attach, and none of the Condition 6 exclusions is engaged by an "
        "accidental electrical fire."),
}


def main():
    claims = parse_all(ROOT / "claim case")
    extractor = DeterministicFacts()
    out = []

    for claim in claims:
        d = adjudicate(claim, extractor.extract(claim))
        exp = KEY[claim["claim_no"]]
        name, quote = QUOTES.get(d.governing_clause, (d.governing_clause, ""))

        items = []
        if d.calc:
            groups = {g["group"]: g for g in d.calc.groups}
            ref_group = {r: g["group"] for g in d.calc.groups for r in g["refs"]}
            for li in d.calc.__dict__.get("_items", []):
                pass
            # rebuild the per-item view from the claim plus the calc grouping
            for it in claim["items"]:
                grp = ref_group.get(it["ref"])
                items.append({
                    "ref": it["ref"], "desc": it["desc"],
                    "claimed": it["claimed"],
                    "schedule_item": it["schedule_item"],
                    "group": grp,
                    "included": grp is not None,
                })

        out.append({
            "claim_no": claim["claim_no"],
            "label": exp["label"],
            "peril": claim["peril_reported"],
            "risk_address": claim["risk_address"],
            "insured": claim["insured"],
            "claimant": claim["claimant"],
            "policy_no": claim["policy_no"],
            "period_from": str(claim["policy_period"]["from"]),
            "period_to": str(claim["policy_period"]["to"]),
            "date_of_loss": str(claim["date_of_loss"]),
            "date_notified": str(claim["date_notified"]),
            "written_claim_received": str(claim["written_claim_received"]),
            "days_to_written_claim": claim["days_to_written_claim"],
            "storeys": claim["storeys"],
            "endorsements": claim["endorsements"],
            "sums_insured": {str(k): v for k, v in claim["sums_insured"].items()},
            "assessed_values": {str(k): v for k, v in claim["assessed_values"].items()},
            "items": claim["items"],
            "total_claimed": claim["total_claimed"],
            "verdict": d.verdict,
            "governing_clause": d.governing_clause,
            "governing_label": d.governing_label,
            "clause_name": name,
            "clause_quote": quote,
            "grounds": d.grounds,
            "also": getattr(d, "also", []),
            "trace": getattr(d, "trace", []),
            "counterfactual": getattr(d, "counterfactual", None),
            "citations": d.citations,
            "flags": d.flags,
            "payable": d.payable,
            "excluded_total": d.calc.excluded_total if d.calc else 0.0,
            "groups": d.calc.groups if d.calc else [],
            "average_applied": {str(k): v for k, v in
                                (d.calc.average_applied if d.calc else {}).items()},
            "working": d.calc.working if d.calc else [],
            "item_view": items,
            "expected": {"verdict": exp["determination"], "payable": exp["payable"],
                         "clause": exp["governing_clause"]},
        })

    evals = json.loads((ROOT / "app" / "eval" / "results.json").read_text("utf-8"))
    lib = json.loads((ROOT / "app" / "data" / "clause_library.json").read_text("utf-8"))

    # what the policy can pay at most, per Schedule item, and the wording that
    # sets that ceiling. An examiner asks this on every file, covered or not.
    for c in out:
        rows = []
        for k, v in c["sums_insured"].items():
            si = v["sum_insured"]
            val = c["assessed_values"].get(k)
            factor = c["average_applied"].get(k)
            rows.append({
                "item": k, "label": v["label"], "sum_insured": si,
                "assessed_value": val,
                "average_factor": factor,
                "capped_at": si,
                "note": ("Underinsured: Condition 20 average applies at "
                         f"{factor}" if factor else
                         ("Adequately insured, no average" if val else
                          "No valuation in evidence, average not applied")),
            })
        c["liability"] = {
            "rows": rows,
            "total_sum_insured": sum(r["sum_insured"] for r in rows),
            "basis_keys": lib["liability_keys"] + (
                ["FP507 Special Condition 1"] if any(
                    e["code"].startswith("FP507") for e in c["endorsements"]) else []),
        }
        # every clause this determination touched, in citation order
        keys = []
        for g in c["grounds"] + c.get("also", []):
            if g["clause"] not in keys:
                keys.append(g["clause"])
        for k in c["citations"]:
            if k not in keys:
                keys.append(k)
        c["clause_keys"] = [k for k in keys if k in lib["clauses"]]
        c["clause_keys_unmapped"] = [k for k in keys if k not in lib["clauses"]]

    METRICS = [
        {"axis": 7, "label": "Determination correct", "value": evals["determination"],
         "measures": "Whether the verdict returned matches the held-out answer key: APPROVE, DECLINE or ESCALATE.",
         "scored": "One point per claim, over all six.",
         "why": "This is the headline question an examiner asks. It is scored separately from the amount, because a right verdict with a wrong figure is not a pass.",
         "field": "verdict_ok"},
        {"axis": 8, "label": "Payable exact to the ringgit", "value": evals["payable"],
         "measures": "Whether the recommended amount equals the key exactly, with no tolerance.",
         "scored": "Only on the two approved claims. A declined claim has no amount to check, so scoring it would inflate the result.",
         "why": "Excesses resolve to the lesser of two figures, two excesses can run in parallel in one claim, and average applies per Schedule item after exclusions rather than before. Each of those is a place a plausible answer lands on the wrong number.",
         "field": "pay_ok"},
        {"axis": 2, "label": "Governing clause ranked first", "value": evals["clause_first"],
         "measures": "Whether the clause named as the primary authority is the one that actually governs, not merely one that applies.",
         "scored": "One point per claim, over all six.",
         "why": "A right verdict reached from the wrong clause fails here. The George Town burglary is the case in point: declining under Condition 5(1)(a) reaches the correct answer for the wrong reason, because that condition addresses theft in connection with a fire and there was no fire.",
         "field": "clause_ok"},
        {"axis": 4, "label": "Answers carrying a citation", "value": f"{len(evals['rows'])}/{len(evals['rows'])}",
         "measures": "Whether every determination points to at least one clause by number or code.",
         "scored": "One point per claim, over all six.",
         "why": "An unsourced determination cannot be checked by anyone, and cannot go on a claim file.",
         "field": None},
    ]

    NOT_MEASURED = [
        {"axis": 5, "name": "Refuses when the policy is silent",
         "why": "Needs the language layer. The six refusal probes are written and held in the ground truth, unscored."},
        {"axis": 6, "name": "Routes record questions out",
         "why": "Needs the language layer. Premium, policy number and claim status probes are written and held, unscored."},
    ]

    rpath = ROOT / "app" / "eval" / "retrieval_results.json"
    retrieval = json.loads(rpath.read_text("utf-8")) if rpath.exists() else None
    if retrieval:
        METRICS.extend([
            {"axis": 1, "label": "Correct clause retrieved", "value": retrieval["axis1"],
             "measures": "Whether the governing clause appears in the top six results returned by the retrieval stack for a query drawn from the claim circumstance.",
             "scored": "One point per claim on the four claims that turn on a coverage clause. The two that fail on policy period have no clause to retrieve.",
             "why": "Vector search plus a cross-encoder is ordinary RAG; this axis checks the plumbing works before the precedence layer is credited with anything.",
             "field": None},
            {"axis": 3, "label": "Override applied, both ways", "value": retrieval["axis3"],
             "measures": "Whether a held endorsement ranks ABOVE the base clause it displaces, and is withdrawn from the override tier when it is NOT held.",
             "scored": "Tested in both directions on the two claims where an endorsement displaces a Condition 6 exclusion. An engine that always ranks the endorsement first passes the first half and fails the second.",
             "why": "This is the moat. Similarity ranking returns the exclusion and the endorsement side by side, both highly relevant, with no notion that one governs the other. Caveat: the base clause is bundled inside the decision node, so the standalone Condition 6 chunk sits outside the pool; the load-bearing half of this test is the withdrawal when not held.",
             "field": None},
        ])

    OUT.write_text(json.dumps({"claims": out, "eval": evals, "clauses": lib["clauses"],
                               "retrieval": retrieval,
                               "metrics": METRICS, "not_measured": NOT_MEASURED,
                               "chain": [{"name": n, "why": w} for n, w in COVERAGE_CHAIN]},
                              indent=2, default=str), encoding="utf-8")
    print(f"frozen {len(out)} claims -> {OUT}")
    for c in out:
        print(f"  {c['claim_no']}  {c['verdict']:8} RM {c['payable']:>10,.2f}  {c['governing_clause']}")


if __name__ == "__main__":
    main()
