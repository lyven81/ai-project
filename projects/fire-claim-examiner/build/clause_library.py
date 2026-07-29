"""
Build the clause library: the exact policy wording behind every citation.

Passages are pulled from the PDF by anchor text, never retyped, so what the UI
shows an examiner is the policy's own language. A detail panel that paraphrases
a clause is worse than useless on a claim file.

Output: app/data/clause_library.json
"""

import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "data" / "clause_library.json"


def policy_text() -> str:
    t = "\n".join((p.extract_text() or "") for p in PdfReader(str(ROOT / "fire policy.pdf")).pages)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*P/GTS/FIR/01-24/V1 Page \d+ of \d+\s*", "\n", t)
    return t


# key -> (display name, kind, anchor, characters to take)
SPEC = {
    "base_insuring_clause": (
        "Operative clause, and the limit of liability", "coverage",
        "the Company will pay or make good to the Insured the actual value", 700),
    "policy_period": (
        "Period of insurance, per the Schedule", "coverage",
        "PROVIDED ALWAYS that the due observance and fulfilment of the terms", 480),
    "peril_not_insured": (
        "Scope of the insuring clause", "coverage",
        "the Company will pay or make good to the Insured the actual value", 420),
    "Condition 2": ("Condition 2, proof of premium payment", "condition",
                    "No payment in respect of any premium shall be deemed", 330),
    "Condition 5(1)(a)": ("Condition 5(1)(a), theft in connection with a fire", "exclusion",
                          "5. (1) This insurance does not cover:", 260),
    "Condition 8(e)": ("Condition 8(e), money and documents", "exclusion",
                       "(e) Securities, obligations, or documents of any kind", 240),
    "Condition 9(b)": ("Condition 9(b), unoccupancy beyond thirty days", "condition",
                       "(b) If the building insured or containing the insured property becomes unoccupied", 230),
    "Condition 9(d)": ("Condition 9(d), transfer of interest", "condition",
                       "(d) If the interest in the property insured pass from the Insured", 190),
    "Condition 12": ("Condition 12, notice and delivery of the claim", "condition",
                     "12. On the happening of any loss or damage the Insured shall forthwith", 560),
    "Condition 17": ("Condition 17, basis of settlement", "liability",
                     "17. In the event of a loss to the property insured", 470),
    "Condition 20": ("Condition 20, condition of average", "liability",
                     "20. If the property hereby insured shall, at the breaking out of any fire", 420),
    "FP503": ("FP503 Storm, Tempest Endorsement", "endorsement",
              "FP503 STORM, TEMPEST ENDORSEMENT", 560),
    "FP503 Special Condition 1": ("FP503 Special Condition 1, causation sequence", "condition",
                                  "1. The Company shall not be liable for any loss or damage caused by water or rain", 620),
    "FP503 SC4(a)": ("FP503 Special Condition 4(a), outdoor fixtures", "exclusion",
                     "4. Unless specifically and separately insured this endorsement does not cover:-", 300),
    "FP504": ("FP504 Flood Endorsement", "endorsement",
              "FP504 FLOOD ENDORSEMENT", 900),
    "FP507B": ("FP507B Bursting or Overflowing of Water Tanks, Apparatus or Pipes", "endorsement",
               "In consideration of an additional premium, the Company hereby agree and declare that the insurance under \nthis Policy shall extend to include loss or damage to the property insured caused by the bursting", 780),
    "FP507B(a)": ("FP507B exclusion (a), untenanted premises", "exclusion",
                  "(a) loss or damage caused whilst the premises are untenanted.", 220),
    "FP507 Special Condition 3": ("FP507 Special Condition 3, defect not remedied after notice", "condition",
                                  "3. The Insured shall use all reasonable diligence and care to keep the premises", 640),
    "FP507 Special Condition 1": ("FP507 Special Condition 1, limit of liability", "liability",
                                  "1. The liability of the Company shall in no case under this endorsement exceed", 190),
    "FP508A.01": ("FP508A.01 Electrical Installations Clause (A)", "endorsement",
                  "This Company is expressly declared to be free from liability for loss of or damage to, any electrical machine", 720),
    "FP510": ("FP510 Subsidence and Landslip Endorsement", "endorsement",
              "FP510 SUBSIDENCE AND LANDSLIP ENDORSEMENT", 560),
    "FP513": ("FP513 Damage by Falling Trees or Branches", "endorsement",
              "FP513 DAMAGE BY FALLING TREES OR BRANCHES", 520),
    "Condition 6(b)": ("Condition 6(b), atmospheric disturbance excluded", "exclusion",
                       "(b) Typhoon, hurricane, tornado, cyclone or other atmospheric disturbance.", 140),
}

# Extra liability-limit provisions surfaced on every claim, because "what is the
# most the policy can pay" is a question an examiner asks on every file.
LIABILITY_KEYS = ["base_insuring_clause", "Condition 20", "Condition 17"]


def main():
    t = policy_text()
    flat = re.sub(r"\s+", " ", t)
    lib = {}
    missing = []

    for key, (name, kind, anchor, take) in SPEC.items():
        a = re.sub(r"\s+", " ", anchor)
        i = flat.find(a)
        if i < 0:
            missing.append(key)
            continue
        lib[key] = {
            "key": key, "name": name, "kind": kind,
            "wording": flat[i:i + take].strip(),
            "source": "P/GTS/FIR/01-24/V1",
        }

    OUT.write_text(json.dumps({"clauses": lib, "liability_keys": LIABILITY_KEYS},
                              indent=2), encoding="utf-8")
    print(f"{len(lib)}/{len(SPEC)} clauses extracted -> {OUT}")
    if missing:
        print("ANCHOR NOT FOUND:", ", ".join(missing))
    for k, v in lib.items():
        print(f"  {k:32} {len(v['wording']):4} chars  {v['wording'][:56]}...")


if __name__ == "__main__":
    main()
