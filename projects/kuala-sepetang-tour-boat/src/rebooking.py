"""
Reallocation: where do the affected passengers actually go?

Naming the nearest workable slot is not advice. If the 15:00 is unworkable and
carries twelve people, and the 11:00 has four seats free, "move them to 11:00"
is not something the operator can do. This module answers the real question:

    for each party sitting in an unworkable departure,
    move them where, or cancel and refund, and say which.

Three hard rules, in this order:

  1. Never displace a passenger who is already booked. A reallocation that
     bumps someone else has not solved the problem, it has moved it.
  2. Never exceed the boat. Twelve seats is twelve seats.
  3. Respect what they booked. A sunset cruise cannot move to 11:00, because
     the sun decides that window. A mangrove cruise can move freely through
     the daylight slots.

Order matters. The hardest party to place is allocated first, otherwise a small
flexible group takes the last seats on the only slot a large locked-in group
could have used. Parties are ranked by how few options they have, not by size.

When nothing fits, the module says cancel and refund and gives the reason,
rather than inventing a slot that does not work.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import config as C
import brain as B
import forecast as F

DATA = Path(__file__).resolve().parent.parent / "data"

# Activities whose window is set by the sun, so they cannot change slot freely.
SUN_LOCKED = {"sunset_cruise", "firefly", "stargazing", "sunset_firefly"}


def load_bookings(anchor: date | None = None) -> dict:
    """
    Sample bookings, hung off a date rather than pinned to one.

    Pinned dates would empty the board the day the window rolls past them, and
    an empty board cannot show the one thing this planner exists to do. The
    offsets are anchored to the first day being viewed, so there are always
    passengers to reason about. Real bookings would carry real dates and this
    function would just read them.
    """
    raw = json.loads((DATA / "bookings.json").read_text(encoding="utf-8"))
    a = anchor or date.today()
    parties = []
    for party in raw["parties"]:
        q = dict(party)
        q["date"] = (a + timedelta(days=q.pop("day_offset"))).isoformat()
        parties.append(q)
    return {"capacity": raw["capacity"], "parties": parties, "anchor": a.isoformat()}


# ---------------------------------------------------------------------------
# Board: every departure across the window, with who is on it and what is left
# ---------------------------------------------------------------------------

def build_board(days: list[dict], bookings: dict) -> dict:
    """
    days: list of payloads from forecast.get_day(), in date order.
    Returns {(date, slot): {...}} with rating, seats taken, seats free,
    and which activities that departure can actually carry.
    """
    cap = bookings["capacity"]
    board = {}

    for day in days:
        for slot in C.SLOTS:
            key = (day["date"], slot["id"])
            verdict = B.score_slot(day, slot["id"], "sheltered")
            fits = {a["activity"]: a["rating"]
                    for a in B.activities_for_slot(day, slot["id"])}
            board[key] = {
                "date": day["date"], "slot": slot["id"], "label": slot["label"],
                "start": slot["start"], "rating": verdict["rating"],
                "shape": verdict["shape"]["shape"],
                "detail": verdict["shape"]["detail"],
                "hazard_stop": verdict["hazard"]["stop"],
                "fits": fits, "cap": cap, "taken": 0, "parties": [],
            }

    for p in bookings["parties"]:
        key = (p["date"], p["slot"])
        if key in board:
            board[key]["taken"] += p["size"]
            board[key]["parties"].append(p)

    for cell in board.values():
        cell["free"] = cell["cap"] - cell["taken"]

    return board


def affected_parties(board: dict) -> list[dict]:
    """Parties sitting in a departure the engine rates unworkable."""
    out = []
    for cell in board.values():
        if cell["rating"] == "poor":
            for p in cell["parties"]:
                out.append(dict(p, from_cell=(cell["date"], cell["slot"]),
                                from_label=cell["label"],
                                reason=cell["detail"],
                                hazard=cell["hazard_stop"]))
    return out


# ---------------------------------------------------------------------------
# Candidate search
# ---------------------------------------------------------------------------

def _day_gap(a: str, b: str) -> int:
    return abs((datetime.strptime(a, "%Y-%m-%d") - datetime.strptime(b, "%Y-%m-%d")).days)


def departure_dt(date_iso: str, slot_id: str) -> datetime:
    """When a departure actually leaves the jetty."""
    slot = next(s for s in C.SLOTS if s["id"] == slot_id)
    return datetime.strptime(f"{date_iso} {slot['start']}", "%Y-%m-%d %H:%M")


def is_reachable(cand_date: str, cand_slot: str,
                 src_date: str, src_slot: str, now: datetime | None = None) -> bool:
    """
    Whether a party sitting on one departure could actually be put on another.

    Two conditions, and the first one is the whole reason this function exists.

    A candidate must leave AFTER the departure being abandoned. The planner
    used to compare only seats, ratings and calendar-day distance, so it would
    cheerfully offer the 09:00 to a party booked on the 13:00 of the same day,
    which reads fine in a table and is impossible on a jetty. Same-day scored
    better than next-day, so it actively preferred going backwards.

    A candidate must also not have left already, with a little notice on top,
    because a boat pulling away in ten minutes is not somewhere twelve people
    who are still at home can be moved to.
    """
    cand = departure_dt(cand_date, cand_slot)
    if cand <= departure_dt(src_date, src_slot):
        return False
    now = now or datetime.now()
    return cand >= now + timedelta(minutes=C.MIN_NOTICE_MINUTES)


def candidates_for(party: dict, board: dict, reserved: dict) -> list[dict]:
    """
    Every departure this party could move to without displacing anyone.

    `reserved` holds seats already promised to earlier reallocations in this
    run, so two moves never claim the same seats.
    """
    out = []
    src_date, src_slot = party["from_cell"]

    for key, cell in board.items():
        if key == party["from_cell"]:
            continue
        if cell["rating"] == "poor":
            continue
        if not is_reachable(cell["date"], cell["slot"], src_date, src_slot):
            continue                                   # already gone, or earlier than the one they are on
        if C.resolve_activity(party["activity"]) not in cell["fits"]:
            continue                                   # the sun, or the clock, says no
        free = cell["free"] - reserved.get(key, 0)
        if free < party["size"]:
            continue

        gap = _day_gap(cell["date"], src_date)
        same_day = cell["date"] == src_date
        # Prefer the same day, then the nearest date, then the better rating.
        score = gap * 2 + B.RANK[cell["rating"]]
        if same_day:
            score -= 1
        out.append({
            "date": cell["date"], "slot": cell["slot"], "label": cell["label"],
            "rating": cell["rating"], "shape": cell["shape"],
            "free_after": free - party["size"], "free_before": free,
            "same_day": same_day, "day_gap": gap, "score": score,
            "activity_rating": cell["fits"][C.resolve_activity(party["activity"])],
        })

    return sorted(out, key=lambda c: (c["score"], c["date"], c["slot"]))


def split_options(party: dict, board: dict, reserved: dict) -> list[dict] | None:
    """
    If no single departure takes the whole party, can two carry it between them?

    Only offered, never chosen automatically. Splitting a school group across
    two boats is the operator's call and the customer's, not the app's.
    """
    src_date, src_slot = party["from_cell"]
    pool = []
    for key, cell in board.items():
        if key == party["from_cell"] or cell["rating"] == "poor":
            continue
        if not is_reachable(cell["date"], cell["slot"], src_date, src_slot):
            continue
        if C.resolve_activity(party["activity"]) not in cell["fits"]:
            continue
        free = cell["free"] - reserved.get(key, 0)
        if free > 0:
            pool.append({"date": cell["date"], "slot": cell["slot"],
                         "label": cell["label"], "rating": cell["rating"],
                         "free": free,
                         "score": _day_gap(cell["date"], src_date) * 2 + B.RANK[cell["rating"]]})
    pool.sort(key=lambda c: (c["score"], -c["free"]))

    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            if pool[i]["free"] + pool[j]["free"] >= party["size"]:
                a, b = pool[i], pool[j]
                take_a = min(a["free"], party["size"])
                return [dict(a, take=take_a), dict(b, take=party["size"] - take_a)]
    return None


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def plan(days: list[dict], bookings: dict) -> dict:
    board = build_board(days, bookings)
    affected = affected_parties(board)

    # Hardest first. A party is hard when it has few places to go, so rank by
    # option count, then by size. Sun-locked activities usually sort to the top
    # without needing a special case, because their option count is small.
    reserved: dict = {}
    scored = []
    for p in affected:
        opts = candidates_for(p, board, reserved)
        scored.append((len(opts), -p["size"], p, opts))
    scored.sort(key=lambda t: (t[0], t[1]))

    results = []
    for _, _, party, _ in scored:
        opts = candidates_for(party, board, reserved)     # recompute, seats moved
        entry = {
            "party": {k: party[k] for k in ("id", "name", "size", "activity")},
            "from": {"date": party["from_cell"][0], "slot": party["from_cell"][1],
                     "label": party["from_label"], "reason": party["reason"],
                     "hazard": party["hazard"]},
            "locked": party["activity"] in SUN_LOCKED,
            "options": opts[:4],
        }

        if opts:
            best = opts[0]
            key = (best["date"], best["slot"])
            reserved[key] = reserved.get(key, 0) + party["size"]
            entry["action"] = "move"
            entry["move_to"] = best
            entry["says"] = _move_sentence(party, best)
        else:
            sp = split_options(party, board, reserved)
            if sp:
                for leg in sp:
                    k = (leg["date"], leg["slot"])
                    reserved[k] = reserved.get(k, 0) + leg["take"]
                entry["action"] = "split"
                entry["split"] = sp
                entry["says"] = _split_sentence(party, sp)
            else:
                entry["action"] = "cancel"
                entry["says"] = _cancel_sentence(party)

        results.append(entry)

    # Report in schedule order so the operator reads it like a day.
    results.sort(key=lambda r: (r["from"]["date"], r["from"]["slot"]))

    moved = sum(1 for r in results if r["action"] == "move")
    split = sum(1 for r in results if r["action"] == "split")
    cancel = sum(1 for r in results if r["action"] == "cancel")
    heads = sum(r["party"]["size"] for r in results)
    saved = sum(r["party"]["size"] for r in results if r["action"] in ("move", "split"))

    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "window": [days[0]["date"], days[-1]["date"]],
        "affected_parties": len(results),
        "affected_passengers": heads,
        "kept": saved, "refunded": heads - saved,
        "moved": moved, "split": split, "cancelled": cancel,
        "no_one_displaced": True,
        "results": results,
        "disclaimer": C.DISCLAIMER,
    }


def _dow(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%A")


def _move_sentence(party: dict, best: dict) -> str:
    when = "later the same day" if best["same_day"] else f"{_dow(best['date'])}"
    return (f"Move {party['name']} ({party['size']}) to {when} {best['label']}. "
            f"Rated {best['rating']}, {best['shape']}. "
            f"{best['free_after']} seats still free after the move, "
            f"and no existing booking is touched.")


def _split_sentence(party: dict, sp: list) -> str:
    legs = " and ".join(f"{l['take']} on {_dow(l['date'])} {l['label']}" for l in sp)
    return (f"No single departure takes all {party['size']}. "
            f"Splitting works: {legs}. This needs the customer's agreement, "
            f"so offer it rather than book it.")


def _cancel_sentence(party: dict) -> str:
    lock = ("The sun sets the window for this trip, so it can only move to the "
            "same departure on another day, and every one of those is either "
            "unworkable or full. ") if party["activity"] in SUN_LOCKED else ""
    return (f"Cancel and refund {party['name']} ({party['size']}). {lock}"
            f"Nothing still to depart in the window takes a party this size "
            f"without bumping someone already booked. Offer a date beyond the "
            f"window, or a different trip, before refunding.")


if __name__ == "__main__":
    bk = load_bookings()
    days = [F.get_day(date(2026, 8, d)) for d in range(24, 29)]
    p = plan(days, bk)

    print(f"Window {p['window'][0]} to {p['window'][1]}")
    print(f"{p['affected_parties']} parties, {p['affected_passengers']} passengers affected")
    print(f"kept {p['kept']}, refunded {p['refunded']}  "
          f"(moved {p['moved']}, split {p['split']}, cancelled {p['cancelled']})")
    print()
    for r in p["results"]:
        pt = r["party"]
        print(f"--- {r['from']['label']} on {_dow(r['from']['date'])} "
              f"| {pt['name']}, {pt['size']} px, {pt['activity']}"
              f"{'  [sun-locked]' if r['locked'] else ''}")
        print(f"    why: {r['from']['reason']}")
        print(f"    ACTION: {r['action'].upper()}")
        print(f"    {r['says']}")
        if r["options"]:
            print("    other options:")
            for o in r["options"][1:4]:
                print(f"      {_dow(o['date'])[:3]} {o['label']:<16} {o['rating']:<9} "
                      f"{o['free_before']} free")
        print()
