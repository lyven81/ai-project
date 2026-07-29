"""
Fire Claim Examiner: the adjudicator.

Splits the job in two, deliberately:

    FACTS   what happened, read out of the circumstance narrative
    RULES   what the policy does with those facts

The language model belongs in FACTS only. It is good at reading a narrative and
answering "was the lot tenanted on the date of loss?". It is not trusted to
decide the claim, because the decision must be reproducible and auditable.

`DeterministicFacts` below is a pattern-based extractor that lets the whole
engine and the eval gate run offline with no key. `LLMFacts` is the swap-in that
answers the same questions with a model. Both satisfy the same interface, so the
rule engine cannot tell them apart, and the rules never change when the
extractor does.
"""

import re
from dataclasses import dataclass, field

from calculator import LineItem, compute

# Which endorsement answers which reported peril. An endorsement not held means
# the base exclusion it was written against stands.
PERIL_ROUTES = {
    "fire": {"group": "BASE", "endorsement": None, "base_peril": True},
    "windstorm": {"group": "FP503", "endorsement": "FP503", "overrides": "Condition 6(b)"},
    "storm": {"group": "FP503", "endorsement": "FP503", "overrides": "Condition 6(b)"},
    "flood": {"group": "FP504", "endorsement": "FP504", "overrides": "Condition 6(b)"},
    "burst water pipe": {"group": "FP507", "endorsement": "FP507", "overrides": None},
    "burglary and theft": {"group": None, "endorsement": None, "not_insured": True},
}

NOTICE_DAYS = 15          # Condition 12
UNOCCUPIED_DAYS = 30      # Condition 9(b)


# --------------------------------------------------------------------- facts
@dataclass
class Facts:
    untenanted_days: int | None = None
    defect_notified_not_remedied: bool = False
    defect_notice_source: str = ""
    storm_damaged_structure_first: bool = False
    water_entered_through_storm_opening: bool = False
    water_origin: str = ""            # inside | outside
    fire_occurred: bool = False
    electrical_origin_machine: str = ""
    outdoor_fixture_refs: list = field(default_factory=list)
    cash_refs: list = field(default_factory=list)
    subsidence_refs: list = field(default_factory=list)
    interest_transferred: bool = False
    written_extension_granted: bool = False


class DeterministicFacts:
    """Offline extractor. Same questions the model is asked, answered by pattern.

    This exists so the eval gate can run with no key and no network. Every
    method is one narrow question about the narrative, never a judgement about
    cover.
    """

    def extract(self, claim: dict) -> Facts:
        # Normalise whitespace FIRST. The narrative is hard-wrapped, so a phrase
        # like "through the opening created by" spans a newline and no flat
        # pattern will ever match it. This cost two false determinations on the
        # first gate run.
        c = re.sub(r"\s+", " ", claim["circumstance"].lower())
        f = Facts()

        m = re.search(r"handed back keys on (\d{1,2} \w+ \d{4})", c)
        if m and "no new tenant had taken occupation" in c:
            from claim_parser import _date
            vac = _date(m.group(1))
            if vac and claim["date_of_loss"]:
                f.untenanted_days = (claim["date_of_loss"] - vac).days

        if ("recommends replacement" in c or "recommend" in c) and \
           ("deferred" in c or "had not been carried out" in c):
            f.defect_notified_not_remedied = True
            f.defect_notice_source = ("insured's own contractor"
                                      if "at her own request" in c or "commissioned by" in c
                                      else "unknown")

        f.storm_damaged_structure_first = bool(
            re.search(r"wind (lifted|displaced)|lifted and displaced", c))
        f.water_entered_through_storm_opening = "through the opening created by" in c

        if "originating from outside" in c or "overtopped its banks" in c or \
           "water entered the ground floor" in c and "rear lane" in c:
            f.water_origin = "outside"
        if "concealed" in c and "pipe" in c and "wall cavity" in c:
            f.water_origin = "inside"

        f.fire_occurred = ("fire broke out" in c or "fire was extinguished" in c
                           or "seat of the fire" in c or "a fire" in c)
        if "there was no fire" in c:
            f.fire_occurred = False

        if "motor windings show evidence of short circuiting" in c:
            m2 = re.search(r"seat of the fire was at the ([a-z ]+?) standing", c)
            f.electrical_origin_machine = m2.group(1).strip() if m2 else "mixer"

        f.interest_transferred = bool(
            re.search(r"transferred from .* to .* with effect", c))
        f.written_extension_granted = "written extension" in c and \
            "no written extension" not in c

        for it in claim["items"]:
            d = it["desc"].lower()
            if any(w in d for w in ("signboard", "awning", "blind")):
                f.outdoor_fixture_refs.append(it["ref"])
            if any(w in d for w in ("cash", "takings", "money")):
                f.cash_refs.append(it["ref"])
            if any(w in d for w in ("boundary wall", "driveway", "footpath")):
                f.subsidence_refs.append(it["ref"])
        return f


# --------------------------------------------------------------------- rules
@dataclass
class Determination:
    claim_no: str
    verdict: str                      # APPROVE | DECLINE | ESCALATE
    governing_clause: str
    governing_label: str
    grounds: list = field(default_factory=list)
    citations: list = field(default_factory=list)
    payable: float = 0.0
    calc: object = None
    flags: list = field(default_factory=list)
    also: list = field(default_factory=list)   # independent grounds not relied on
    counterfactual: object = None             # what it would have paid but for the ground above
    trace: list = field(default_factory=list)  # the ordered gates, and where it stopped


# THE COVERAGE CHAIN. Order is the whole point, and it is the basis on which
# every claim is approved or rejected: the determination is always the FIRST
# gate that fails. A gate placed later cannot undo a wrong answer produced by
# one placed earlier, and reordering any two of these flips the outcome on at
# least one of the six claims:
#
#   period before peril      claim 1 is a covered fire, 18 months out of period
#   peril before quantum     claim 4 would otherwise be priced, though a fire
#                            policy never covers burglary at any figure
#   notice before endorsement  claim 5 holds FP504 and the flood is squarely
#                            within it, yet Condition 12 defeats it
#   held before satisfied    claim 2 holds exactly the right endorsement and
#                            still fails on that endorsement's own exclusion
COVERAGE_CHAIN = [
    ("Period of insurance", "Did the loss occur inside the period? Nothing else is asked until this passes."),
    ("Peril insured", "Is the reported peril within the insuring clause, or brought in by an endorsement?"),
    ("Conditions precedent", "Condition 12 notice. A condition precedent defeats an otherwise covered peril."),
    ("Endorsement held", "Is the endorsement that answers this peril on the Schedule?"),
    ("Endorsement satisfied", "Holding it is not satisfying it. Its own exclusions and special conditions are tested against the facts."),
    ("Item admitted", "Each item claimed is tested separately; some fall out while the claim itself stands."),
]


def secondary_grounds(claim: dict, facts: Facts, governing: str) -> list:
    """Independent grounds the claim would also have failed on.

    The engine returns on the first ground that disposes of the claim, which is
    correct: the period check must not be reached past. But a declinature letter
    names every independent ground, so an examiner is not surprised later by one
    that was never written down. These are recorded, never relied on.
    """
    out = []
    lo, hi = claim["policy_period"]["from"], claim["policy_period"]["to"]
    dol = claim["date_of_loss"]
    peril = (claim["peril_reported"] or "").lower()
    route = next((v for k, v in PERIL_ROUTES.items() if k in peril), None)
    days = claim.get("days_to_written_claim")

    def add(clause, reason):
        if clause != governing:
            out.append({"clause": clause, "reason": reason})

    if lo and hi and dol and not (lo <= dol <= hi):
        add("policy_period", f"Loss {dol} falls outside the period {lo} to {hi}.")
    if route is None or route.get("not_insured"):
        add("peril_not_insured",
            f"'{claim['peril_reported']}' is not an insured peril under a fire "
            f"policy and no endorsement on the Schedule extends cover to it.")
    if days is not None and days > NOTICE_DAYS and not facts.written_extension_granted:
        add("Condition 12",
            f"Written claim delivered {days} days after the loss, against the "
            f"{NOTICE_DAYS} day requirement, with no written extension.")
    if facts.cash_refs:
        add("Condition 8(e)",
            "Cash and takings are claimed but no money item appears on the "
            "Schedule; Condition 8(e) excludes coins and paper money.")
    if facts.interest_transferred:
        add("Condition 9(d)",
            "Interest in the insured property passed from the Insured with no "
            "endorsement recording the change.")
    if facts.untenanted_days and facts.untenanted_days > UNOCCUPIED_DAYS:
        add("Condition 9(b)",
            f"Building unoccupied {facts.untenanted_days} days, beyond the "
            f"{UNOCCUPIED_DAYS} day limit, without the Company's sanction.")
    return out


def price_items(claim: dict, facts: Facts, group: str, held: set) -> list:
    """Apply item-level treatment: which clause admits or excludes each item.

    Shared by the payable path and the counterfactual path, so a declined claim
    is priced by exactly the same rules that would have priced it if it had
    survived. A counterfactual computed by a different route is not evidence.
    """
    items = []
    circ = claim["circumstance"].lower()
    for it in claim["items"]:
        li = LineItem(it["ref"], it["desc"], it["claimed"],
                      it["schedule_item"], "covered", "base", group)
        d = it["desc"].lower()

        if it["ref"] in facts.outdoor_fixture_refs and group == "FP503":
            li.treatment, li.clause = "excluded", "FP503 SC4(a)"
        elif it["ref"] in facts.cash_refs:
            li.treatment, li.clause = "excluded", "Condition 8(e)"
        elif it["ref"] in facts.subsidence_refs and group == "FP504":
            li.treatment, li.clause = "excluded", "FP504 SC1(c)"
        elif facts.electrical_origin_machine and \
                facts.electrical_origin_machine.split()[-1] in d:
            li.treatment, li.clause = "excluded", "FP508A.01"
        elif "branch" in circ and any(w in d for w in ("porch", "gutter")) \
                and "FP513" in held:
            li.group, li.clause = "FP513", "FP513"
        elif group == "BASE" and facts.electrical_origin_machine:
            li.clause = "FP508A.01 proviso"
        elif group != "BASE":
            li.clause = group

        items.append(li)
    return items


def counterfactual(claim: dict, facts: Facts, blocked_by: str) -> dict | None:
    """What the policy would have paid but for the ground that disposed of it.

    Not a payable figure and never presented as one. It sizes the exposure so a
    senior examiner can weigh a referral, which matters most on the Kampar
    flood: the Company may still allow further time in writing under Condition
    12, and if it does, this is the number that becomes live.
    """
    peril = (claim["peril_reported"] or "").lower()
    route = next((v for k, v in PERIL_ROUTES.items() if k in peril), None)
    if route is None or route.get("not_insured"):
        return {"available": False,
                "reason": "No basis to price. The peril is outside the insuring "
                          "clause of a fire policy, so there is no cover to "
                          "quantify at any figure."}

    held = set(claim["endorsement_codes"])
    group = route["group"]
    if not route.get("base_peril"):
        code = route["endorsement"]
        if code == "FP507":
            storeys = (claim["storeys"] or {}).get("count") or 0
            code = "FP507A" if storeys > 5 else "FP507B"
            group = code
        if code not in held:
            return {"available": False,
                    "reason": f"No basis to price. {code} is not held, so the "
                              f"base exclusion stands regardless of "
                              f"{blocked_by}."}

    items = price_items(claim, facts, group, held)
    sums = {k: v["sum_insured"] for k, v in claim["sums_insured"].items()}
    calc = compute(items, sums, claim["assessed_values"])
    return {
        "available": True,
        "amount": calc.payable,
        "blocked_by": blocked_by,
        "basis": f"Priced under {group} on the same rules the payable path uses.",
        "groups": calc.groups,
        "excluded_total": calc.excluded_total,
        "working": calc.working,
        "items": [{"ref": i.ref, "desc": i.desc, "claimed": i.claimed,
                   "schedule_item": i.schedule_item, "treatment": i.treatment,
                   "clause": i.clause, "group": i.group} for i in items],
    }


def adjudicate(claim: dict, facts: Facts) -> Determination:
    held = set(claim["endorsement_codes"])
    grounds, cites, flags = [], [], []

    trace = []

    def step(name, result, detail):
        trace.append({"step": len(trace) + 1, "name": name,
                      "result": result, "detail": detail})

    def ground(clause, text):
        grounds.append({"clause": clause, "reason": text})
        cites.append(clause)

    def decline(governing, label):
        for nm, _why in COVERAGE_CHAIN[len(trace):]:
            step(nm, "not_reached", "Not asked: the claim stopped above.")
        d = Determination(claim["claim_no"], "DECLINE", governing, label,
                          grounds, sorted(set(cites)), 0.0, None, flags)
        d.trace = trace
        d.also = secondary_grounds(claim, facts, governing)
        d.counterfactual = counterfactual(claim, facts, governing)
        return d

    # -- 1. policy period, always first ------------------------------------
    lo, hi = claim["policy_period"]["from"], claim["policy_period"]["to"]
    dol = claim["date_of_loss"]
    if lo and hi and dol and not (lo <= dol <= hi):
        when = "after expiry" if dol > hi else "before inception"
        step("Period of insurance", "fail",
             f"Loss {dol} is outside {lo} to {hi} ({when}).")
        ground("policy_period",
               f"Loss {dol} falls outside the period {lo} to {hi} ({when}).")
        if facts.interest_transferred:
            ground("Condition 9(d)",
                   "Interest in the insured property passed from the Insured "
                   "with no endorsement recording the change.")
        return decline("policy_period", "Loss outside the period of insurance")

    step("Period of insurance", "pass", f"Loss {dol} falls inside {lo} to {hi}.")

    # -- 2. is the peril insured at all? -----------------------------------
    peril = (claim["peril_reported"] or "").lower()
    route = next((v for k, v in PERIL_ROUTES.items() if k in peril), None)
    if route is None or route.get("not_insured"):
        step("Peril insured", "fail",
             f"'{claim['peril_reported']}' is not within the insuring clause "
             f"and no endorsement on the Schedule extends to it.")
        ground("peril_not_insured",
               f"'{claim['peril_reported']}' is not an insured peril under a "
               f"fire policy and no endorsement extends cover to it.")
        if facts.cash_refs:
            ground("Condition 8(e)",
                   "Cash and takings excluded; no money item on the Schedule.")
        return decline("peril_not_insured", "Peril outside the insuring clause")

    step("Peril insured", "pass",
         f"'{claim['peril_reported']}' routes to "
         f"{route.get('endorsement') or 'the base insuring clause'}.")

    # -- 3. Condition 12, notice of loss ------------------------------------
    days = claim.get("days_to_written_claim")
    if days is not None and days > NOTICE_DAYS and not facts.written_extension_granted:
        step("Conditions precedent", "fail",
             f"Written claim delivered on day {days}, against the "
             f"{NOTICE_DAYS} day requirement. Condition 12 is a condition "
             f"precedent and defeats an otherwise covered peril.")
        ground("Condition 12",
               f"Written claim delivered {days} days after the loss, against "
               f"the {NOTICE_DAYS} day requirement, with no written extension. "
               f"Condition 12 is a condition precedent: no claim is payable "
               f"unless its terms have been complied with.")
        flags.append("The Company may still allow further time in writing. "
                     "Refer to a senior examiner before issuing the declinature.")
        return decline("Condition 12", "Condition 12 breached, condition precedent")

    step("Conditions precedent", "pass",
         (f"Written claim delivered on day {days}, within {NOTICE_DAYS} days."
          if days is not None else "No notice defect on the file."))

    # -- 4. endorsement resolution and its own conditions -------------------
    group = route["group"]
    if route.get("base_peril"):
        step("Endorsement held", "pass",
             "None required: fire attaches under the base insuring clause.")
        step("Endorsement satisfied", "pass",
             "No endorsement conditions to satisfy.")
        ground("base_insuring_clause",
               "Fire is the core insured peril; no endorsement is required and "
               "no Condition 6 exclusion is engaged.")
    else:
        code = route["endorsement"]
        if code == "FP507":
            storeys = (claim["storeys"] or {}).get("count") or 0
            mezz = (claim["storeys"] or {}).get("mezzanine")
            code = "FP507A" if (storeys > 5 or mezz and storeys >= 5) else "FP507B"
            group = code
        if code not in held:
            step("Endorsement held", "fail", f"{code} is not on the Schedule.")
            base = route.get("overrides") or "the base policy"
            ground(base, f"{code} is not held, so {base} stands and the loss "
                         f"is not covered.")
            return decline(base, f"{code} not held")

        step("Endorsement held", "pass",
             f"{code} is on the Schedule and overrides "
             f"{route.get('overrides') or 'the base position'}.")
        ground(code, f"{code} is held and overrides "
                     f"{route.get('overrides') or 'the base position'}.")

        if code in ("FP507A", "FP507B"):
            if facts.water_origin == "outside":
                flags.append("Water originated outside the building; FP504 may "
                             "be the governing endorsement, not FP507.")
            if facts.untenanted_days and facts.untenanted_days > 0:
                step("Endorsement satisfied", "fail",
                     f"{code} is held, but its exclusion (a) applies: the "
                     f"premises were untenanted {facts.untenanted_days} days.")
                ground(f"{code}(a)",
                       f"Premises untenanted at the date of loss, "
                       f"{facts.untenanted_days} days since handover. "
                       f"{code} exclusion (a) applies.")
                if facts.untenanted_days > UNOCCUPIED_DAYS:
                    ground("Condition 9(b)",
                           f"Building unoccupied more than {UNOCCUPIED_DAYS} "
                           f"days without the Company's sanction endorsed.")
                if facts.defect_notified_not_remedied:
                    ground("FP507 Special Condition 3",
                           "A defect was notified and not remedied before the "
                           "loss occurred at that same pipework.")
                    flags.append(
                        "Special Condition 3 speaks of notice from the Company "
                        "or any person or public body; here the report was "
                        f"commissioned from the {facts.defect_notice_source}. "
                        "Whether that is 'any person' is arguable. The "
                        "determination does not rest on it.")
                return decline(f"{code}(a)",
                               f"{code} exclusion (a), premises untenanted")

        if code == "FP503":
            if not (facts.storm_damaged_structure_first and
                    facts.water_entered_through_storm_opening):
                step("Endorsement satisfied", "fail",
                     "FP503 is held, but Special Condition 1 is not satisfied.")
                ground("FP503 Special Condition 1",
                       "The building must first sustain actual damage to roof "
                       "or walls by the direct force of the peril before water "
                       "damage to the interior is covered. Not established.")
                return decline("FP503 Special Condition 1",
                               "Causation sequence not satisfied")
            step("Endorsement satisfied", "pass",
                 "FP503 Special Condition 1 satisfied: the structure was "
                 "damaged first, and water then entered through those openings.")
            ground("FP503 Special Condition 1",
                   "Sequence satisfied: wind damaged the roof structure first, "
                   "and water then entered through those openings.")

    # -- 5. item level treatment -------------------------------------------
    items = price_items(claim, facts, group, held)

    for li in items:
        if li.treatment == "excluded":
            cites.append(li.clause)

    if facts.electrical_origin_machine:
        ground("FP508A.01",
               "Excludes the particular machine in which the electrical fault "
               "originated, and expressly preserves cover for other property "
               "damaged by the fire it set up.")

    sums = {k: v["sum_insured"] for k, v in claim["sums_insured"].items()}
    if claim["assessed_values"]:
        ground("Condition 20",
               "Average applied per Schedule item; every item is separately "
               "subject to the Condition.")

    calc = compute(items, sums, claim["assessed_values"])

    governing = "base_insuring_clause" if group == "BASE" else group
    label = ("Fire, attaching under the base insuring clause with no "
             "endorsement required" if group == "BASE" else f"Covered under {group}")

    excl = [i for i in items if i.treatment == "excluded"]
    step("Item admitted", "pass",
         (f"{len(items) - len(excl)} of {len(items)} items admitted, "
          f"{len(excl)} excluded by clause." if excl
          else f"All {len(items)} items admitted."))
    while len(trace) < len(COVERAGE_CHAIN):
        step(COVERAGE_CHAIN[len(trace)][0], "pass", "")

    d = Determination(claim["claim_no"], "APPROVE", governing, label, grounds,
                      sorted(set(cites)), calc.payable, calc, flags)
    d.trace = trace
    d.also = secondary_grounds(claim, facts, governing)
    d.counterfactual = None
    return d
