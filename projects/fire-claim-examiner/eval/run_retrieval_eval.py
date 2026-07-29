"""
Layer 5 eval: axes 1 and 3, which the metadata-only engine could not score.

    axis 1  correct clause retrieved      is the governing clause in the top k?
    axis 3  correct endorsement overrides is the endorsement ranked ABOVE the
                                          base clause it displaces, when held,
                                          and BELOW it when not held?

Axis 3 is the one that matters. It is trivially satisfiable by an engine that
hard-codes the answer, so it is tested both ways round: the same query is run
with the endorsement held and not held, and the ordering must flip. An engine
that always puts the endorsement first passes the first half and fails the
second.
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

from retrieval import PolicyRetriever          # noqa: E402

K = 6

# claim -> (query drawn from the circumstance, endorsement, base clause it
#           displaces, chunk that must be retrieved)
CASES = [
    {"claim": "CLM-2022-06033", "label": "Ipoh windstorm",
     "query": "wind lifted and displaced roof tiles, then rain entered the roof "
              "space through that opening and came through the ceiling",
     "endorsement": "FP503", "base": "CONDITION-6", "peril": "storm",
     "expect": ["DECISION-STORM-FP503", "ENDORSEMENT-FP503"]},
    {"claim": "CLM-2023-12440", "label": "Kampar flood",
     "query": "the river overtopped its banks and water entered the ground floor "
              "from the rear lane to a depth of 1.2 metres",
     "endorsement": "FP504", "base": "CONDITION-6", "peril": "flood",
     "expect": ["DECISION-FLOOD-FP504", "ENDORSEMENT-FP504"]},
    {"claim": "CLM-2023-11207", "label": "Taiping burst pipe",
     "query": "a concealed water supply pipe burst at a corroded joint inside "
              "the wall cavity while the shop lot was untenanted",
     "endorsement": "FP507B", "base": None, "peril": "water_pipe",
     "expect": ["ENDORSEMENT-FP507B"]},
    {"claim": "CLM-2024-03187", "label": "Sungai Petani bakery fire",
     "query": "fire started at a dough mixer from short circuiting in the motor "
              "windings and spread to the oven and shelving",
     "endorsement": "FP508A.01", "base": None, "peril": "electrical",
     "expect": ["ENDORSEMENT-FP508A.01"]},
]

# procedural grounds still have to be findable
CLAUSE_PROBES = [
    ("the written claim was delivered 31 days after the loss", "CONDITION-12"),
    ("cash and takings kept in a drawer were stolen", "CONDITION-8"),
    ("the shop lot stood empty for 48 days before the loss", "CONDITION-9"),
    ("the property was worth more than the sum insured", "CONDITION-20"),
]


def main():
    r = PolicyRetriever(verbose=True)
    print()
    rows, a1, a3 = [], 0, 0

    print("=" * 78)
    print("AXIS 1  correct clause retrieved (top %d)" % K)
    print("-" * 78)
    for c in CASES:
        res = r.search(c["query"], held={c["endorsement"]}, k=K, peril=c["peril"])
        ids = [x["chunk_id"] for x in res]
        hit = any(e in ids for e in c["expect"])
        a1 += hit
        pos = next((i + 1 for i, x in enumerate(ids) if x in c["expect"]), None)
        print(f"  {'ok ' if hit else 'XX '} {c['claim']:16} {c['label']:26} "
              f"rank {pos if pos else '-'}   {ids[0]}")
        rows.append({"claim": c["claim"], "axis1": hit, "rank": pos, "top": ids[0]})

    print()
    print("=" * 78)
    print("AXIS 3  endorsement overrides the base policy, tested BOTH ways")
    print("-" * 78)
    for c in CASES:
        if not c["base"]:
            print(f"  --  {c['claim']:16} {c['label']:26} no base clause displaced")
            continue
        held = r.search(c["query"], held={c["endorsement"]}, k=12, peril=c["peril"])
        free = r.search(c["query"], held=set(), k=12, peril=c["peril"])

        def rank_of(res, pred):
            return next((i for i, x in enumerate(res) if pred(x)), 99)

        end_h = rank_of(held, lambda x: x["code"] == c["endorsement"]
                        and x["effective_authority"] == "override")
        base_h = rank_of(held, lambda x: x["chunk_id"] == c["base"])
        # not held: the endorsement must NOT be sitting in the override tier
        still_override = any(x["code"] == c["endorsement"]
                             and x["type"] != "coverage_decision"
                             and x["effective_authority"] == "override" for x in free)

        ok = (end_h < base_h) and not still_override
        a3 += ok
        print(f"  {'ok ' if ok else 'XX '} {c['claim']:16} {c['label']:26} "
              f"held: {c['endorsement']} at {end_h} vs {c['base']} at {base_h}"
              f"   not held: override withdrawn = {not still_override}")
        rows.append({"claim": c["claim"], "axis3": ok})

    print()
    print("=" * 78)
    print("CLAUSE PROBES  procedural grounds must remain findable")
    print("-" * 78)
    probe_ok = 0
    for q, want in CLAUSE_PROBES:
        ids = [x["chunk_id"] for x in r.search(q, held=set(), k=K)]
        hit = want in ids
        probe_ok += hit
        print(f"  {'ok ' if hit else 'XX '} {want:14} rank "
              f"{ids.index(want) + 1 if hit else '-'}   {q[:52]}")

    n3 = len([c for c in CASES if c["base"]])
    print()
    print("=" * 78)
    print(f"axis 1  correct clause retrieved      {a1}/{len(CASES)}")
    print(f"axis 3  override applied, both ways   {a3}/{n3}")
    print(f"        procedural clause probes      {probe_ok}/{len(CLAUSE_PROBES)}")
    gate = a1 == len(CASES) and a3 == n3 and probe_ok == len(CLAUSE_PROBES)
    print("=" * 78)
    print("RETRIEVAL GATE PASSED" if gate else "RETRIEVAL GATE FAILED")
    print("=" * 78)

    (BASE / "eval" / "retrieval_results.json").write_text(json.dumps({
        "axis1": f"{a1}/{len(CASES)}", "axis3": f"{a3}/{n3}",
        "probes": f"{probe_ok}/{len(CLAUSE_PROBES)}",
        "gate_passed": gate, "rows": rows,
        "stack": {"embed": "all-MiniLM-L6-v2", "rerank": "ms-marco-MiniLM-L-6-v2",
                  "store": "Qdrant (in-memory)", "chunks": len(r.chunks)},
    }, indent=2), encoding="utf-8")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
