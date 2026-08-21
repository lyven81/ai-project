"""
The brain: reading a two-hour departure window.

Nothing here calls a language model. Given the same forecast, this file
returns the same verdict every time, against thresholds the operator owns.
That repeatability is the whole reason the project exists: a chat model
eyeballing a forecast gives a different answer every run and no basis the
operator can show anyone.

Four things are worked out that appear nowhere in the data:

  shape       where in the two hours the rain sits
  hazard      thunderstorm and squall, kept separate from comfort
  rating      good, marginal or poor against the operator's thresholds
  confidence  how much the lead time earns

The asymmetry that matters: rain at the start is cheap, because the boat is
at the jetty and a short delay fixes it. Rain at the end is expensive,
because the return leg is the exposed part and the boat is furthest from
cover. So `arrives` rates worse than `clears` at identical millimetres.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import combined as CB
import config as C
import forecast as F
import moon as M

RANK = {"good": 0, "marginal": 1, "poor": 2}
UNRANK = {v: k for k, v in RANK.items()}


# ---------------------------------------------------------------------------
# Shape
# ---------------------------------------------------------------------------

def classify_shape(window: dict) -> dict:
    """
    Which of five shapes the window takes.

    Averaging a two-hour window throws away the part the operator needs, so
    the buckets are read in order instead.
    """
    rain = [r or 0.0 for r in (window.get("rain") or window.get("precipitation") or [])]
    n = len(rain)
    if n == 0:
        return {"shape": "dry", "wet_buckets": 0, "total_buckets": 0,
                "total_mm": 0.0, "detail": "No precipitation data for this window."}

    wet = [r >= C.WET_BUCKET_MM for r in rain]
    n_wet = sum(wet)
    total_mm = round(sum(rain), 2)
    times = window.get("time") or []

    def clock(i):
        return times[i][11:16] if i < len(times) else "?"

    if n_wet == 0:
        shape, detail = "dry", "Dry through the whole window."
    elif n_wet >= C.THROUGHOUT_SHARE * n:
        shape = "throughout"
        detail = f"Wet in {n_wet} of {n} buckets, end to end."
    else:
        half = n // 2
        first, second = sum(wet[:half]), sum(wet[half:])
        if first and not second:
            shape = "clears"
            last_wet = max(i for i, w in enumerate(wet) if w)
            detail = f"Wet at the start, drying from about {clock(last_wet + 1)}."
        elif second and not first:
            shape = "arrives"
            first_wet = min(i for i, w in enumerate(wet) if w)
            detail = (f"Dry at the start, rain from about {clock(first_wet)}, "
                      f"which lands on the return leg.")
        else:
            shape = "intermittent"
            detail = f"Showers on and off, {n_wet} of {n} buckets wet."

    return {
        "shape": shape,
        "wet_buckets": n_wet,
        "total_buckets": n,
        "total_mm": total_mm,
        "resolution": window.get("resolution"),
        "detail": detail,
        "return_leg_exposed": shape in ("arrives", "throughout"),
        "contingency": C.CONTINGENCY[shape],
    }


# ---------------------------------------------------------------------------
# Hazard. Reported as a stop, never as a score.
# ---------------------------------------------------------------------------

def assess_hazard(window: dict) -> dict:
    codes = [c for c in (window.get("weather_code") or window.get("h_weather_code") or []) if c is not None]
    gusts = [g for g in (window.get("wind_gusts_10m") or []) if g is not None]
    cape = [c for c in (window.get("h_cape") or []) if c is not None]

    thunder = [c for c in codes if c in C.HAZARD["thunder_codes"]]
    max_gust = max(gusts) if gusts else None
    max_cape = max(cape) if cape else None

    reasons = []
    stop = False
    if thunder:
        stop = True
        reasons.append("Thunderstorm in the window. Lightning on open water is the hazard, not the rain.")
    if max_gust is not None and max_gust >= C.HAZARD["gust_stop_kmh"]:
        stop = True
        reasons.append(f"Gusts reach {max_gust:.0f} km/h, at or above the {C.HAZARD['gust_stop_kmh']} km/h stop.")

    watch = []
    if not thunder and max_cape is not None and max_cape >= C.HAZARD["cape_watch_jkg"]:
        watch.append(
            f"Atmosphere is primed for storms (CAPE {max_cape:.0f} J/kg) even though no "
            f"thunderstorm is forecast. Worth a look at the sky before boarding."
        )

    return {"stop": stop, "reasons": reasons, "watch": watch,
            "max_gust_kmh": max_gust, "max_cape_jkg": max_cape}


# ---------------------------------------------------------------------------
# Comfort rating against the operator's thresholds
# ---------------------------------------------------------------------------

def rate_comfort(window: dict, exposure: str, hours: float = 2.0) -> dict:
    t = C.THRESHOLDS[exposure]

    gusts = [g for g in (window.get("wind_gusts_10m") or []) if g is not None]
    rain = [r or 0.0 for r in (window.get("rain") or window.get("precipitation") or [])]
    probs = [p for p in (window.get("h_precipitation_probability") or []) if p is not None]
    vis = [v for v in (window.get("h_visibility") or []) if v is not None]

    max_gust = max(gusts) if gusts else 0.0
    mm_per_hour = (sum(rain) / hours) if rain else 0.0
    max_prob = max(probs) if probs else 0
    min_vis = min(vis) if vis else None

    drivers = []
    rating = "good"

    def bump(level, why):
        nonlocal rating
        if RANK[level] > RANK[rating]:
            rating = level
        drivers.append(why)

    if max_gust >= t["gust_poor_kmh"]:
        bump("poor", f"gusts {max_gust:.0f} km/h, over the {t['gust_poor_kmh']} km/h limit for {exposure} water")
    elif max_gust >= t["gust_marginal_kmh"]:
        bump("marginal", f"gusts {max_gust:.0f} km/h")

    if mm_per_hour >= t["rain_poor_mm_per_hour"]:
        bump("poor", f"rain {mm_per_hour:.1f} mm/h")
    elif mm_per_hour > 0:
        bump("marginal", f"rain {mm_per_hour:.1f} mm/h")

    # Probability is a heads-up; precipitation is the event. In the tropics a
    # high chance of rain routinely sits alongside zero forecast accumulation,
    # because the model expects a shower somewhere in the hour without putting
    # measurable rain in the bucket. Letting probability alone reach "poor"
    # would mark most monsoon afternoons unworkable and the operator would
    # stop reading the app. So it can only confirm rain that is already there.
    if max_prob >= t["prob_poor_pct"]:
        if mm_per_hour > 0:
            bump("poor", f"{max_prob}% chance of rain, and rain already in the window")
        else:
            bump("marginal", f"{max_prob}% chance of a shower, though no measurable "
                             f"rain is forecast in the window")
    elif max_prob >= t["prob_marginal_pct"]:
        bump("marginal", f"{max_prob}% chance of rain")

    if min_vis is not None and min_vis <= t["visibility_poor_m"]:
        bump("poor", f"visibility down to {min_vis/1000:.1f} km")

    return {"rating": rating, "drivers": drivers, "max_gust_kmh": round(max_gust, 1),
            "rain_mm_per_hour": round(mm_per_hour, 2), "max_rain_probability_pct": max_prob,
            "min_visibility_m": min_vis}


# ---------------------------------------------------------------------------
# Confidence by lead time
# ---------------------------------------------------------------------------

def confidence_for(lead: int) -> dict:
    lead = max(lead, 0)
    for band in C.CONFIDENCE_TIERS:
        if lead <= band["max_lead_days"]:
            return dict(band, lead_days=lead, measured=C.CONFIDENCE_MEASURED)
    last = C.CONFIDENCE_TIERS[-1]
    return dict(last, lead_days=lead, measured=C.CONFIDENCE_MEASURED)


# ---------------------------------------------------------------------------
# One slot
# ---------------------------------------------------------------------------

def _slot(slot_id: str) -> dict:
    for s in C.SLOTS:
        if s["id"] == slot_id:
            return s
    valid = ", ".join(s["id"] for s in C.SLOTS)
    raise F.ForecastError(
        f"'{slot_id}' is not a departure. The boat runs six: {valid} "
        f"(that is {', '.join(s['start'] for s in C.SLOTS)})."
    )


def score_slot(day: dict, slot_id: str, exposure: str = "sheltered") -> dict:
    s = _slot(slot_id)
    window = F.slice_window(day, s["start"], s["end"])

    shape = classify_shape(window)
    hazard = assess_hazard(window)
    comfort = rate_comfort(window, exposure)

    rating = comfort["rating"]
    adjust = None
    # Rain that arrives late costs more than the same rain arriving early,
    # but only once there is enough of it to matter. A trace in the final
    # buckets is not a reason to lose the slot.
    late_mm = _second_half_mm(window)
    if shape["shape"] == "arrives" and rating != "poor":
        if late_mm >= C.ARRIVES_PENALTY_MIN_MM:
            rating = UNRANK[min(RANK[rating] + 1, 2)]
            adjust = (f"downgraded one step: {late_mm:.1f} mm arrives on the return leg, "
                      f"at or over the {C.ARRIVES_PENALTY_MIN_MM} mm mark")
        else:
            adjust = (f"rain arrives late but only {late_mm:.1f} mm, under the "
                      f"{C.ARRIVES_PENALTY_MIN_MM} mm mark, so no downgrade")
    if hazard["stop"]:
        rating = "poor"

    # What the hour before and after are doing. Rain at 08:00 means a choppy,
    # muddy river at 09:00; rain at 11:00 catches the boat coming in.
    before = F.hour_value(day, _shift(s["start"], -1), "rain")
    after = F.hour_value(day, s["end"], "rain")

    conf = confidence_for(day.get("lead_days", 0))
    return {
        "slot": s["id"], "label": s["label"], "date": day["date"],
        "exposure": exposure,
        "rating": rating,
        "rating_adjusted": adjust,
        "hazard": hazard,
        "shape": shape,
        "comfort": comfort,
        "approach": {"hour_before_rain_mm": before, "hour_after_rain_mm": after,
                     "note": _edge_note(before, after)},
        "confidence": conf,
        # Stage B measured that timing inside the window is not forecastable
        # past tomorrow. Beyond that the shape is computed but must not be
        # shown as a claim, so the payload says so rather than leaving the
        # caller to remember.
        "shape_reliable": conf.get("shape_shown", False),
        "shape_caveat": None if conf.get("shape_shown") else (
            f"At {conf['lead_days']} days out the forecast cannot place rain inside "
            f"a two-hour window better than guesswork. Read this as "
            f"{'rain expected' if shape['shape'] != 'dry' else 'no rain expected'}, "
            f"not as timing."),
        "disclaimer": C.DISCLAIMER,
    }


def _second_half_mm(window: dict) -> float:
    """How much rain falls in the back half of the window, where the boat is
    furthest from cover."""
    rain = [r or 0.0 for r in (window.get("rain") or window.get("precipitation") or [])]
    if not rain:
        return 0.0
    return round(sum(rain[len(rain) // 2:]), 2)


def _shift(hhmm: str, hours: int) -> str:
    h, m = (int(x) for x in hhmm.split(":"))
    return f"{(h + hours) % 24:02d}:{m:02d}"


def _edge_note(before, after) -> str:
    bits = []
    if before and before > 0:
        bits.append("rain in the hour before, so expect a choppy and muddy river at the start")
    if after and after > 0:
        bits.append("rain in the hour after, which can catch the boat coming in")
    return "; ".join(bits) if bits else "clear either side of the window"


# ---------------------------------------------------------------------------
# All six, ranked, with the nearest better alternative
# ---------------------------------------------------------------------------

def compare_slots(day: dict, exposure: str = "sheltered") -> dict:
    scored = [score_slot(day, s["id"], exposure) for s in C.SLOTS]

    def key(v):
        return (RANK[v["rating"]], v["shape"]["total_mm"], v["comfort"]["max_gust_kmh"])

    order = sorted(scored, key=key)
    best_ids = [v["slot"] for v in order if v["rating"] != "poor"]

    for v in scored:
        if v["rating"] == "poor":
            v["alternative"] = _nearest_better(v["slot"], scored)
        else:
            v["alternative"] = None

    return {
        "date": day["date"],
        "lead_days": day.get("lead_days", 0),
        "confidence": confidence_for(day.get("lead_days", 0)),
        "slots": scored,
        "ranked": [v["slot"] for v in order],
        "workable": best_ids,
        "summary": _day_summary(scored),
        "sunrise": day["daily"]["sunrise"], "sunset": day["daily"]["sunset"],
        "moon": M.describe(datetime.strptime(day["date"], "%Y-%m-%d").date()),
        "disclaimer": C.DISCLAIMER,
    }


def _nearest_better(slot_id: str, scored: list) -> dict | None:
    """
    The next workable departure on this day, looking FORWARD only.

    It used to sort on absolute distance, so a party on the 13:00 was offered
    the 09:00 of the same day. A departure that has already sailed is not an
    alternative to one that has not, however close it is on the clock.

    Returning None is a real answer: it means nothing later that day works, and
    the caller should look at another day rather than be handed a slot that
    cannot be taken.
    """
    ids = [s["id"] for s in C.SLOTS]
    i = ids.index(slot_id)
    later = [v for v in scored
             if v["rating"] != "poor" and ids.index(v["slot"]) > i]
    if not later:
        return None
    best = sorted(later, key=lambda v: (ids.index(v["slot"]) - i, RANK[v["rating"]]))[0]
    gap = ids.index(best["slot"]) - i
    return {
        "slot": best["slot"], "label": best["label"], "rating": best["rating"],
        "shape": best["shape"]["shape"],
        "note": f"{gap * 2} hours later",
    }


def _day_summary(scored: list) -> str:
    good = [v["label"] for v in scored if v["rating"] == "good"]
    poor = [v["label"] for v in scored if v["rating"] == "poor"]
    parts = []
    if good:
        parts.append(f"{len(good)} clear: {', '.join(good)}")
    if poor:
        parts.append(f"{len(poor)} not workable: {', '.join(poor)}")
    if not parts:
        parts.append("all six marginal")
    return ". ".join(parts) + "."


# ---------------------------------------------------------------------------
# Activity fit
# ---------------------------------------------------------------------------

def _activity_window(activity: dict, day: dict) -> tuple[str, str]:
    kind, a, b = activity["window"]
    if kind == "clock":
        return a, b
    sunset = day["daily"]["sunset"]
    if not sunset:
        raise F.ForecastError(f"No sunset time for {day['date']}, so the "
                              f"{activity['name']} window cannot be worked out.")
    base = datetime.strptime(sunset, "%Y-%m-%dT%H:%M")
    start = base + timedelta(minutes=a)
    end = base + timedelta(minutes=b)
    return start.strftime("%H:%M"), end.strftime("%H:%M")


def _combined_for_slot(slot_id: str):
    for tid, trip in getattr(C, "COMBINED_TRIPS", {}).items():
        if trip["slot"] == slot_id:
            return tid, trip
    return None, None


def activities_for_slot(day: dict, slot_id: str) -> list[dict]:
    """
    What the boat actually runs in this window.

    Where a departure sells as one combined trip, that trip is returned instead
    of its parts, so the board cannot offer a product the operator retired.
    """
    tid, trip = _combined_for_slot(slot_id)
    if trip:
        r = CB.score_combined(day, tid)
        notes = list(r["phases"]["firefly"]["why"])
        notes.append(r["bonus"]["say"])
        notes.append(r["phases"]["firefly"]["moon_note"])
        return [{
            "activity": tid, "name": trip["name"],
            "exposure": trip["phases"][1]["exposure"],
            "activity_window": r["phases"]["firefly"]["window"],
            "overlap_minutes": r["phases"]["firefly"]["minutes"],
            "rating": r["overall"], "notes": notes,
            "drivers": r["phases"]["firefly"]["why"],
            "tell_the_guest": r["tell_the_guest"],
        }]

    return _plain_activities_for_slot(day, slot_id)


def _plain_activities_for_slot(day: dict, slot_id: str) -> list[dict]:
    """The original per-activity match, for every departure without a combined trip."""
    s = _slot(slot_id)
    s_start, s_end = F._minutes(s["start"]), F._minutes(s["end"])
    on = datetime.strptime(day["date"], "%Y-%m-%d").date()
    moon_pct = M.illumination_pct(on)

    out = []
    for a in C.ACTIVITIES:
        if a["id"] in getattr(C, "SUPERSEDED_ACTIVITIES", ()):
            continue
        try:
            a_start, a_end = _activity_window(a, day)
        except F.ForecastError:
            continue
        overlap = min(s_end, F._minutes(a_end)) - max(s_start, F._minutes(a_start))
        if overlap < C.MIN_OVERLAP_MINUTES:
            continue

        # An anchored activity needs its moment inside the departure, not just
        # an overlapping window. Sunset at 19:26 does not make the 19:00 boat a
        # sunset cruise; the guests would board into dusk and sail into dark.
        anchor = C.ACTIVITY_ANCHORS.get(a["id"])
        if anchor:
            at = day["daily"].get(anchor)
            if not at:
                continue
            if not (s_start <= F._minutes(at[11:16]) < s_end):
                continue

        verdict = score_slot(day, slot_id, a["exposure"])
        rating, notes = verdict["rating"], []
        rules = C.ACTIVITY_RULES.get(a["id"], {})

        cloud = [c for c in (F.slice_window(day, s["start"], s["end"]).get("h_cloud_cover") or []) if c is not None]
        avg_cloud = sum(cloud) / len(cloud) if cloud else None

        # Cloud and moon describe the view, not whether the boat can go out.
        # They add a note the operator can pass to the guest. They never move
        # the rating, which stays with rain, wind, thunderstorm and visibility.
        if a["id"] == "sunset_cruise" and avg_cloud is not None:
            if avg_cloud > rules["cloud_poor_above_pct"]:
                notes.append(f"cloud {avg_cloud:.0f}%, the sunset will not show")
            elif rules["cloud_good_band_pct"][0] <= avg_cloud <= rules["cloud_good_band_pct"][1]:
                notes.append(f"cloud {avg_cloud:.0f}%, good chance of a sunset")
            else:
                notes.append(f"cloud {avg_cloud:.0f}%, a plain sunset at best")

        if a["id"] == "stargazing" and avg_cloud is not None:
            notes.append(f"cloud {avg_cloud:.0f}%, moon {moon_pct}%")

        if a["id"] == "firefly" and moon_pct > rules.get("moon_marginal_above_pct", 75):
            notes.append(f"moon {moon_pct}%, a thinner display than on a dark night")

        out.append({
            "activity": a["id"], "name": a["name"], "exposure": a["exposure"],
            "activity_window": f"{a_start} to {a_end}",
            "overlap_minutes": overlap,
            "rating": rating,
            "notes": notes,
            "drivers": verdict["comfort"]["drivers"],
        })

    return sorted(out, key=lambda x: (RANK[x["rating"]], -x["overlap_minutes"]))


if __name__ == "__main__":
    day = F.get_day(date.today())
    print(f"--- {day['date']} (lead {day['lead_days']}) ---")
    cmp_ = compare_slots(day)
    print("summary:", cmp_["summary"])
    print("moon:", cmp_["moon"]["illumination_pct"], "%", cmp_["moon"]["phase"])
    print("confidence:", cmp_["confidence"]["tier"], "|", cmp_["confidence"]["booking"])
    print()
    for v in cmp_["slots"]:
        alt = v["alternative"]
        print(f"{v['label']:<16} {v['rating']:<9} {v['shape']['shape']:<13} "
              f"gust {v['comfort']['max_gust_kmh']:>5.1f}  "
              f"{v['shape']['detail']}")
        if v["hazard"]["stop"]:
            print(f"                 STOP: {v['hazard']['reasons'][0]}")
        if alt:
            print(f"                 alternative: {alt['label']} ({alt['rating']}, {alt['note']})")
    print()
    print("activities that fit 19:00:")
    for a in activities_for_slot(day, "1900"):
        print(f"  {a['name']:<24} {a['rating']:<9} {a['activity_window']}  {'; '.join(a['notes'])}")
