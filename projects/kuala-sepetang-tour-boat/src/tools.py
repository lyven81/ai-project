"""
The tool layer: four tools, two of them ours.

  get_current_datetime   what day it is, and the date of each day ahead
  get_boat_conditions    everything about the water, at whatever grain is asked
  web_search             everything the weather cannot answer
  text editor            the message the operator sends the customer

This used to be seven schemas, four of which touched weather. That was the
problem. Four overlapping weather tools meant the model had to pick correctly
between them before it could be right about anything, and the descriptions had
to carry paragraphs of what-this-is-NOT-for to stop it guessing.

The four are now one. `get_boat_conditions` reads its own grain from the
arguments: a time gives one departure, a bare date gives the day, a date range
gives the outlook. The functions behind it did not change and are still here,
they are simply no longer choices the model has to make.

Two things moved out of the model's hands at the same time, both of them
previously prompt faults:

  reallocation range   the model used to pass a window and would pick one day,
                       forcing a split a wider window would have avoided. The
                       lookahead is now fixed in code.
  slot resolution      "around 4 PM" is not a departure. The tool maps a clock
                       time to the real departure and says which one it chose,
                       rather than the model guessing a slot id.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import config as C
import brain as B
import forecast as F
import rebooking as R
from editor import TextEditorTool, EditorError

REPLY_ROOT = Path(__file__).resolve().parent.parent / "data" / "replies"


def _safe_session(session: str) -> str:
    """One folder per visitor. Without this, two people using the demo edit the
    same files and clobber each other."""
    keep = "".join(ch for ch in (session or "demo") if ch.isalnum() or ch in "-_")
    return (keep or "demo")[:40]


def editor_for(session: str) -> TextEditorTool:
    return TextEditorTool(REPLY_ROOT / _safe_session(session))

_SLOT_IDS = ", ".join(f'"{s["id"]}" ({s["start"]})' for s in C.SLOTS)
_ACT_IDS = ", ".join(a["id"] for a in C.ACTIVITIES)


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

# Malaysia is UTC+8 all year with no daylight saving, so a fixed offset is
# exact here and avoids depending on the tzdata package being present in the
# image. If this app is ever pointed at a location that observes DST, this is
# the line that has to become a real timezone lookup.
MYT = timezone(timedelta(hours=8), name="Asia/Kuala_Lumpur")

WEEKDAY_LOOKAHEAD = 8


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> dict:
    """
    What day and time it is now at the jetty.

    This exists because the model cannot know it and does not reckon it well.
    Asked about "this Sunday" without this tool, it answers from the shape of
    its training data, which is right often enough to look fine and wrong often
    enough to matter.

    So the reply does the arithmetic too. `upcoming` names the next eight days
    by weekday, which is how customers actually ask ("this Sunday", "next
    Tuesday"), and turns a calculation into a lookup.
    """
    if not date_format or not date_format.strip():
        raise ValueError(
            "date_format cannot be empty. Use a strftime pattern such as "
            "%Y-%m-%d %H:%M:%S, or omit it for the default."
        )

    now = datetime.now(MYT)
    today = now.date()

    upcoming = {}
    for i in range(WEEKDAY_LOOKAHEAD):
        d = today + timedelta(days=i)
        label = "today" if i == 0 else "tomorrow" if i == 1 else d.strftime("%A")
        # First occurrence wins, so "Sunday" means the next Sunday, not the one
        # eight days out.
        upcoming.setdefault(label, d.isoformat())

    return {
        "now": now.strftime(date_format),
        "date": today.isoformat(),
        "weekday": today.strftime("%A"),
        "time": now.strftime("%H:%M"),
        "timezone": C.LOCATION["timezone"],
        "location": C.LOCATION["name"],
        "upcoming": upcoming,
        "forecast_reaches": (today + timedelta(days=F.MAX_LEAD_DAYS)).isoformat(),
        "note": (
            "Resolve every relative date from this reply, never from memory. "
            "Dates before " + today.isoformat() + " are history and cannot be "
            "used to plan a departure."
        ),
    }


def get_outlook(start_date: str, end_date: str | None = None) -> dict:
    start = F.parse_date(start_date)
    end = F.parse_date(end_date) if end_date else start
    if end < start:
        raise F.ForecastError(
            f"{end_date} comes before {start_date}. Put the earlier date first."
        )
    span = (end - start).days
    if span > 9:
        raise F.ForecastError(
            f"That is {span + 1} days. Ask for 10 or fewer at a time, "
            f"or the answer is too coarse to be useful."
        )
    out = []
    for day in F.get_days(start, span + 1):
        d = F.parse_date(day["date"])
        cmp_ = B.compare_slots(day)
        conf = B.confidence_for(day["lead_days"])
        workable = [v["slot"] for v in cmp_["slots"] if v["rating"] != "poor"]
        out.append({
            "date": d.isoformat(), "lead_days": day["lead_days"],
            "workable_departures": len(workable), "of": len(C.SLOTS),
            "not_workable": [v["label"] for v in cmp_["slots"] if v["rating"] == "poor"],
            "summary": cmp_["summary"],
            "sunset": cmp_["sunset"][11:], "moon_pct": cmp_["moon"]["illumination_pct"],
            "confidence": {"tier": conf["tier"], "booking": conf["booking"],
                           "timing_reliable": conf.get("shape_shown", False)},
        })
    return {"days": out, "disclaimer": C.DISCLAIMER}


def get_slot_forecast(date: str, slot: str, exposure: str = "sheltered") -> dict:
    day = F.get_day(F.parse_date(date))
    v = B.score_slot(day, slot, exposure)
    v["activities_that_fit"] = [
        {"name": a["name"], "rating": a["rating"], "notes": a["notes"]}
        for a in B.activities_for_slot(day, slot)
    ]
    return v


def compare_slots(date: str) -> dict:
    day = F.get_day(F.parse_date(date))
    c = B.compare_slots(day)
    return {
        "date": c["date"], "summary": c["summary"], "confidence": c["confidence"],
        "sunrise": c["sunrise"][11:], "sunset": c["sunset"][11:], "moon": c["moon"],
        "ranked_best_first": c["ranked"], "workable": c["workable"],
        "slots": [{
            "slot": v["slot"], "label": v["label"], "rating": v["rating"],
            "shape": v["shape"]["shape"], "detail": v["shape"]["detail"],
            "shape_reliable": v["shape_reliable"], "shape_caveat": v["shape_caveat"],
            "contingency": v["shape"]["contingency"],
            "max_gust_kmh": v["comfort"]["max_gust_kmh"],
            "rain_mm_per_hour": v["comfort"]["rain_mm_per_hour"],
            "hazard_stop": v["hazard"]["stop"], "hazard_reasons": v["hazard"]["reasons"],
            "alternative": v["alternative"],
        } for v in c["slots"]],
        "disclaimer": C.DISCLAIMER,
    }


def plan_reallocation(start_date: str, end_date: str) -> dict:
    from datetime import timedelta
    start, end = F.parse_date(start_date), F.parse_date(end_date)
    if end < start:
        raise F.ForecastError(f"{end_date} comes before {start_date}.")
    days = [F.get_day(start + timedelta(days=i)) for i in range((end - start).days + 1)]
    p = R.plan(days, R.load_bookings(start))
    return {
        "window": p["window"],
        "affected_parties": p["affected_parties"],
        "affected_passengers": p["affected_passengers"],
        "kept": p["kept"], "refunded": p["refunded"],
        "moved": p["moved"], "split": p["split"], "cancelled": p["cancelled"],
        "no_one_displaced": p["no_one_displaced"],
        "results": [{
            "party": r["party"], "from": r["from"], "sun_locked": r["locked"],
            "action": r["action"], "recommendation": r["says"],
            "other_options": [{"date": o["date"], "label": o["label"],
                               "rating": o["rating"], "seats_free": o["free_before"]}
                              for o in r["options"][1:4]],
        } for r in p["results"]],
        "disclaimer": p["disclaimer"],
    }


def run_text_editor(tool_input: dict, session: str = "demo") -> str:
    return editor_for(session).run(tool_input)


# ---------------------------------------------------------------------------
# The one weather tool. Everything above is now an implementation detail of it.
# ---------------------------------------------------------------------------

# How far past the affected day the planner may look for seats. Fixed here
# rather than asked of the model: when it chose the window itself it picked one
# day and split parties that three days would have kept together.
RELOCATION_LOOKAHEAD_DAYS = 3


def _parse_clock(value: str) -> int:
    """
    Minutes past midnight, from whatever a person or a model types.

    Accepts 15:00, 1500, 3pm, 3 PM, 3.30pm, 16:00. Raises with the six real
    departures listed, because a caller that got this wrong can fix it from
    the list.
    """
    raw = str(value).strip().lower().replace(".", ":")
    pm = raw.endswith("pm")
    am = raw.endswith("am")
    if pm or am:
        raw = raw[:-2].strip()

    try:
        if ":" in raw:
            h, m = raw.split(":", 1)
            hour, minute = int(h), int(m or 0)
        elif len(raw) == 4 and raw.isdigit():
            hour, minute = int(raw[:2]), int(raw[2:])
        else:
            hour, minute = int(raw), 0
    except ValueError:
        raise F.ForecastError(
            f"Could not read '{value}' as a time. Use 24 hour form such as 15:00, "
            f"or a plain hour such as 4pm. The boat runs at "
            f"{', '.join(s['start'] for s in C.SLOTS)}."
        ) from None

    if pm and hour < 12:
        hour += 12
    if am and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise F.ForecastError(f"'{value}' is not a real time of day.")
    return hour * 60 + minute


def _departure_for(value: str) -> tuple[dict, str | None]:
    """
    The departure a requested time actually belongs to.

    Customers ask for "around 4 PM". The boat does not run at 4 PM. So the tool
    resolves the request to a real departure and hands back a note saying it
    did, which the assistant is told to repeat: a silently shifted booking is
    how someone ends up at the jetty an hour late.
    """
    want = _parse_clock(value)
    starts = [(s, F._minutes(s["start"])) for s in C.SLOTS]

    for s, start in starts:
        if start <= want < F._minutes(s["end"]):
            exact = want == start
            return s, None if exact else (
                f"{value} falls inside the {s['label']} departure, which leaves at "
                f"{s['start']}. Quote {s['start']}, not {value}.")

    nearest, gap = min(
        ((s, abs(start - want)) for s, start in starts), key=lambda t: t[1])
    return nearest, (
        f"There is no departure at {value}. The boat runs at "
        f"{', '.join(s['start'] for s in C.SLOTS)}. The closest is {nearest['start']}, "
        f"{gap} minutes away. Quote {nearest['start']}.")


def _relocation_for(target_date, slot_id: str) -> dict | None:
    """
    Where the people on one unworkable departure actually go.

    Whole party or nothing. `candidates_for` already refuses any departure
    without room for all of them, so this reports a move, or reports honestly
    that the window holds nothing, rather than offering a partial seat count.
    """
    start = target_date
    days = F.get_days(start, RELOCATION_LOOKAHEAD_DAYS + 1)
    p = R.plan(days, R.load_bookings(start))

    mine = [r for r in p["results"]
            if r["from"]["date"] == start.isoformat() and r["from"]["slot"] == slot_id]
    if not mine:
        return None

    out = []
    for r in mine:
        entry = {"party": r["party"]["name"], "size": r["party"]["size"],
                 "action": r["action"]}
        if r["action"] == "move":
            b = r["move_to"]
            entry["move_to"] = {"date": b["date"], "departure": b["label"],
                                "rating": b["rating"], "same_day": b["same_day"],
                                "seats_free_after": b["free_after"]}
            entry["whole_party"] = True
        elif r["action"] == "split":
            # Offered, never chosen. The operator decides whether a group will
            # accept being separated.
            entry["whole_party"] = False
            entry["split_offer"] = [{"date": l["date"], "departure": l["label"],
                                     "take": l["take"]} for l in r["split"]]
            entry["note"] = ("No single departure in the next "
                             f"{RELOCATION_LOOKAHEAD_DAYS} days seats all "
                             f"{r['party']['size']}. Splitting needs their agreement.")
        else:
            entry["whole_party"] = False
            entry["note"] = r["says"]
        out.append(entry)
    return {"lookahead_days": RELOCATION_LOOKAHEAD_DAYS, "parties": out}


def get_boat_conditions(date: str, time: str | None = None,
                        end_date: str | None = None,
                        exposure: str = "sheltered") -> dict:
    """
    Conditions on the water at Kuala Sepetang, at whatever grain was asked for.

    One departure, one day, or a run of days. The arguments decide, so the
    caller never has to choose between four similar tools and get it wrong.
    """
    start = F.parse_date(date)

    # ---- a run of days: can we take a booking at all ----------------------
    if end_date:
        out = get_outlook(date, end_date)
        out["grain"] = "outlook"
        return out

    # ---- one departure ----------------------------------------------------
    if time:
        slot, note = _departure_for(time)
        v = get_slot_forecast(start.isoformat(), slot["id"], exposure)
        v["grain"] = "departure"
        v["asked_for"] = time
        v["departure"] = slot["label"]
        if note:
            v["time_resolved"] = note
        if v["rating"] == "poor":
            v["relocation"] = _relocation_for(start, slot["id"])
        return v

    # ---- the whole day ----------------------------------------------------
    c = compare_slots(start.isoformat())
    c["grain"] = "day"
    for row in c["slots"]:
        if row["rating"] == "poor":
            row["relocation"] = _relocation_for(start, row["slot"])
    return c


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

GET_CURRENT_DATETIME = {
    "name": "get_current_datetime",
    "description": (
        "The current date, weekday and time at the jetty, plus the calendar date "
        "of each of the next eight days by name. Call this FIRST, before any "
        "weather tool, whenever the question involves a relative date such as "
        "today, tonight, tomorrow, this Sunday, next weekend, or in three days. "
        "Do not work such a date out from memory: use the `upcoming` map in the "
        "reply, which gives the exact date for each weekday name. The reply also "
        "gives the last date the forecast reaches. Anything earlier than the "
        "date returned here is history and cannot be used to plan a departure."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "Optional strftime pattern for the `now` field, for "
                               "example %H:%M for the time alone. The date, weekday "
                               "and upcoming dates come back regardless.",
                "default": "%Y-%m-%d %H:%M:%S",
            },
        },
        "required": [],
    },
}

GET_BOAT_CONDITIONS = {
    "name": "get_boat_conditions",
    "description": (
        "Live and forecast conditions on the water at Kuala Sepetang, read "
        "against the operator's own thresholds. This is the ONLY source of "
        "weather: never use web search for a forecast. It answers at three "
        "grains and picks the grain from the arguments you pass. "
        "Give a date AND a time for one departure: the rating, where the rain "
        "sits inside the two hours, gusts, visibility, any thunderstorm stop, "
        "what the departure can carry, and, when it cannot run and has "
        "passengers, where the whole party goes instead. "
        "Give a date ALONE for that day's six departures ranked against each "
        "other, which is what answers 'plan today' or 'which departure should "
        "they take'. "
        "Give a date AND an end_date to look across several days, which is what "
        "answers 'can we promise them Saturday'. "
        "A clock time does not have to be a departure time: pass what the "
        "customer asked for and the reply resolves it to the real departure."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "The date, as YYYY-MM-DD. Resolve any relative date "
                               "with get_current_datetime first; do not work it out "
                               "yourself. The words today and tomorrow are accepted.",
            },
            "time": {
                "type": "string",
                "description": "Optional. A clock time such as 15:00 or 4pm, for ONE "
                               "departure. It need not match a departure time: the "
                               "reply says which departure it resolved to, and you "
                               "must quote that departure time to the customer rather "
                               "than the time they asked for. Omit this to get the "
                               "whole day.",
            },
            "end_date": {
                "type": "string",
                "description": "Optional. Last date, as YYYY-MM-DD, for a multi-day "
                               "outlook. At most 10 days. Do not combine with time.",
            },
            "exposure": {
                "type": "string", "enum": ["sheltered", "open"],
                "description": "sheltered for mangrove channels, the fishing village "
                               "and the fish farm. open for the estuary, dolphin runs, "
                               "fishing trips and the long Kuala Sangga leg. Defaults "
                               "to sheltered.",
                "default": "sheltered",
            },
        },
        "required": ["date"],
    },
}

WEB_SEARCH = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 4,
    "allowed_domains": ["met.gov.my", "malaysia.gov.my", "perak.gov.my",
                        "moe.gov.my", "tourism.gov.my", "bernama.com"],
}

TEXT_EDITOR = {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}

CUSTOM_SCHEMAS = [GET_CURRENT_DATETIME, GET_BOAT_CONDITIONS]
ALL_SCHEMAS = CUSTOM_SCHEMAS + [WEB_SEARCH, TEXT_EDITOR]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def run_tool(tool_name: str, tool_input: dict, session: str = "demo"):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    if tool_name == "get_boat_conditions":
        return get_boat_conditions(**tool_input)
    if tool_name in ("get_outlook", "get_slot_forecast", "compare_slots",
                     "plan_reallocation"):
        raise ValueError(
            f"'{tool_name}' was merged into get_boat_conditions. Call that "
            f"instead: a date and a time for one departure, a date alone for the "
            f"day, a date and an end_date for several days."
        )
    if tool_name in ("str_replace_based_edit_tool", "str_replace_editor"):
        return run_text_editor(tool_input, session)
    raise ValueError(
        f"'{tool_name}' is not a tool here. Available: get_current_datetime, "
        f"get_boat_conditions, str_replace_based_edit_tool, web_search."
    )


if __name__ == "__main__":
    print("--- get_outlook, 3 days ---")
    o = get_outlook("2026-08-24", "2026-08-26")
    for d in o["days"]:
        print(f"  {d['date']} {d['workable_departures']}/6 workable, "
              f"{d['confidence']['tier']}, timing reliable: {d['confidence']['timing_reliable']}")

    print("\n--- get_slot_forecast 2026-08-24 1500 ---")
    v = get_slot_forecast("2026-08-24", "1500")
    print(f"  {v['rating']} / {v['shape']['shape']} / {v['shape']['detail']}")
    print(f"  reliable: {v['shape_reliable']}  caveat: {v['shape_caveat']}")

    print("\n--- compare_slots 2026-08-24 ---")
    c = compare_slots("2026-08-24")
    print(f"  {c['summary']}  ranked: {c['ranked_best_first']}")

    print("\n--- plan_reallocation 24 to 28 ---")
    p = plan_reallocation("2026-08-24", "2026-08-28")
    print(f"  {p['affected_passengers']} affected, kept {p['kept']}, refunded {p['refunded']}")
    for r in p["results"]:
        print(f"    {r['party']['name']:<20} {r['action']}")

    print("\n--- error messages the model can act on ---")
    for fn, args in [(get_slot_forecast, {"date": "2026-08-24", "slot": "1600"}),
                     (get_outlook, {"start_date": "next tuesday"}),
                     (get_outlook, {"start_date": "2027-01-01"})]:
        try:
            fn(**args)
            print("    NO ERROR")
        except Exception as e:
            print(f"    {e}")
