"""
Relocation gate: a party can only be moved to a departure it could actually take.

This exists because of a defect that shipped. The planner compared seats,
ratings and calendar-day distance, and scored same-day above next-day, so it
offered the 09:00 to a party booked on the 13:00 of the same morning. Three of
five proposed moves on a live week were backwards in time. It reads perfectly
well in a table, and it is impossible on a jetty.

Every property below would have caught it. They run over the real forecast for
the days ahead, so the gate is scored against live weather rather than a fixture.

    forward         a move always leaves after the departure it replaces
    not departed    a move is never onto a boat that has already gone
    capacity        no departure is taken past its seats
    no displacement no existing booking is bumped to make room
    activity fits   a party is never moved to a departure that cannot carry it
    seats reconcile everyone affected is moved, split, or refunded, once
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import config as C
import forecast as F
import rebooking as R

WINDOW_DAYS = 7
RESULTS = Path(__file__).resolve().parent.parent / "results"


def run() -> dict:
    start = date.today()
    days = F.get_days(start, WINDOW_DAYS)
    bookings = R.load_bookings(start)
    board = R.build_board(days, bookings)
    plan = R.plan(days, bookings)

    violations: list[str] = []
    now = datetime.now()

    # ---- forward, and not already departed --------------------------------
    for r in plan["results"]:
        src = R.departure_dt(r["from"]["date"], r["from"]["slot"])
        legs = []
        if r["action"] == "move":
            legs = [(r["move_to"]["date"], r["move_to"]["slot"], r["party"]["size"])]
        elif r["action"] == "split":
            legs = [(l["date"], l["slot"], l["take"]) for l in r["split"]]

        for d, s, _ in legs:
            cand = R.departure_dt(d, s)
            if cand <= src:
                violations.append(
                    f"BACKWARDS: {r['party']['name']} {r['from']['date']} "
                    f"{r['from']['slot']} to {d} {s}")
            if cand < now:
                violations.append(
                    f"ALREADY DEPARTED: {r['party']['name']} sent to {d} {s}, "
                    f"which left before {now:%Y-%m-%d %H:%M}")
            if cand < now + timedelta(minutes=C.MIN_NOTICE_MINUTES):
                violations.append(
                    f"TOO SHORT NOTICE: {r['party']['name']} sent to {d} {s}, "
                    f"under the {C.MIN_NOTICE_MINUTES} minute rule")

    # ---- capacity, displacement, activity fit -----------------------------
    added: dict[tuple, int] = {}
    for r in plan["results"]:
        legs = []
        if r["action"] == "move":
            legs = [(r["move_to"]["date"], r["move_to"]["slot"], r["party"]["size"])]
        elif r["action"] == "split":
            legs = [(l["date"], l["slot"], l["take"]) for l in r["split"]]
        for d, s, n in legs:
            added[(d, s)] = added.get((d, s), 0) + n
            cell = board[(d, s)]
            if C.resolve_activity(r["party"]["activity"]) not in cell["fits"]:
                violations.append(
                    f"ACTIVITY: {r['party']['name']} ({r['party']['activity']}) "
                    f"moved to {d} {s}, which cannot carry it")
            if cell["rating"] == "poor":
                violations.append(f"UNWORKABLE TARGET: {r['party']['name']} to {d} {s}")

    for key, n in added.items():
        cell = board[key]
        if cell["taken"] + n > cell["cap"]:
            violations.append(
                f"CAPACITY: {key} would hold {cell['taken'] + n} of {cell['cap']}")

    # ---- everyone accounted for, once -------------------------------------
    heads = sum(r["party"]["size"] for r in plan["results"])
    if plan["kept"] + plan["refunded"] != heads:
        violations.append(
            f"RECONCILE: kept {plan['kept']} + refunded {plan['refunded']} "
            f"!= {heads} affected")

    seen = [r["party"]["id"] for r in plan["results"]]
    if len(seen) != len(set(seen)):
        violations.append("DUPLICATE: a party appears twice in the plan")

    moves = sum(1 for r in plan["results"] if r["action"] == "move")
    out = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "window": plan["window"],
        "affected_parties": plan["affected_parties"],
        "affected_passengers": plan["affected_passengers"],
        "moved": moves, "split": plan["split"], "cancelled": plan["cancelled"],
        "kept": plan["kept"], "refunded": plan["refunded"],
        "violations": violations,
        "gate": "PASS" if not violations else "FAIL",
    }

    print(f"Relocation gate, {plan['window'][0]} to {plan['window'][1]}")
    print(f"  {plan['affected_parties']} parties, {plan['affected_passengers']} passengers affected")
    print(f"  moved {moves}, split {plan['split']}, cancelled {plan['cancelled']}")
    print(f"  kept {plan['kept']}, refunded {plan['refunded']}")
    print()
    for r in plan["results"]:
        if r["action"] == "move":
            m = r["move_to"]
            print(f"    {r['party']['name']:<20} {r['from']['date']} {r['from']['slot']}"
                  f"  ->  {m['date']} {m['slot']}")
        else:
            print(f"    {r['party']['name']:<20} {r['from']['date']} {r['from']['slot']}"
                  f"  ->  {r['action'].upper()}")
    print()
    if violations:
        print(f"  {len(violations)} violation(s):")
        for v in violations:
            print("    " + v)
    else:
        print("  no violations")
    print()
    print("=" * 68)
    print(f"GATE: {out['gate']}")
    print("=" * 68)

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "relocation-gate.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\nsaved -> results/relocation-gate.json")
    return out


if __name__ == "__main__":
    sys.exit(0 if run()["gate"] == "PASS" else 1)
