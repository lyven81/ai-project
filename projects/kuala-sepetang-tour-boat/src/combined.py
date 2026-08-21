"""
Scoring the Evening Firefly Run.

One departure, two halves, different needs. The sunset half is open water
looking west and lives or dies on cloud. The firefly half is sheltered channels
in the dark and lives or dies on rain, wind and moonlight.

Corrected 21 Aug 2026 on the operator's instruction, after this module drifted.

The app exists to answer whether the boat should go out and whether the trip
gets rained on. It had started grading how pretty the evening would be, letting
cloud thickness and moon brightness pull a rating down. Neither decides whether
a boat can sail, and an evening ride on a calm dry river is a good ride whatever
the moon is doing.

So the rating now comes from the passage only: rain, wind, thunderstorm. Cloud
and moon are reported to the operator as things to tell the guest, and can never
cost a night.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import config as C
import forecast as F
import moon as M

RANK = {"good": 0, "marginal": 1, "poor": 2}
UNRANK = {v: k for k, v in RANK.items()}


def _clock(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def phase_windows(day: dict, trip: dict) -> list[dict]:
    """Turn the sunset-relative definitions into clock times for this date."""
    slot = next(s for s in C.SLOTS if s["id"] == trip["slot"])
    sunset = datetime.strptime(day["daily"]["sunset"], "%Y-%m-%dT%H:%M")
    d_start = sunset.replace(hour=int(slot["start"][:2]), minute=int(slot["start"][3:]))
    d_end = sunset.replace(hour=int(slot["end"][:2]), minute=int(slot["end"][3:]))

    out = []
    for ph in trip["phases"]:
        start = (d_start if ph.get("from") == "departure_start"
                 else sunset + timedelta(minutes=ph["from_sunset_offset"]))
        end = (d_end if ph.get("to") == "departure_end"
               else sunset + timedelta(minutes=ph["to_sunset_offset"]))
        start, end = max(start, d_start), min(end, d_end)
        out.append({**ph, "start": _clock(start), "end": _clock(end),
                    "minutes": max(0, int((end - start).total_seconds() // 60))})
    return out


def _sunset_note(w: dict, t: dict) -> dict:
    """
    Whether the sun is likely to show. A note for the guest, never a rating.

    The passage decision is made on the firefly half, which covers the same
    river in the same weather. Rating the sunset separately would let a cloudy
    sky cancel a perfectly good boat ride.
    """
    cloud = [c for c in (w.get("h_cloud_cover") or []) if c is not None]
    avg = sum(cloud) / len(cloud) if cloud else None
    if avg is None:
        return {"state": "unknown", "say": "No cloud data for the sunset window.",
                "avg_cloud_pct": None}
    lo, hi = t["cloud_good_band_pct"]
    if avg > t["cloud_poor_above_pct"]:
        state, say = "no", "Sunset will not show. Do not mention it."
    elif lo <= avg <= hi:
        state, say = "likely", "Sunset should show. Mention it, do not promise it."
    else:
        state, say = "possible", "Sunset may show. Worth a word, no promise."
    return {"state": state, "say": say, "avg_cloud_pct": round(avg, 0)}


def _score_firefly(w: dict, t: dict, moon_pct: int) -> dict:
    """
    Rates the firefly half on whether the boat should go out and whether the
    trip gets rained on. Nothing else.

    The moon is reported, never rated. A calm dry evening on the river is a
    good evening whatever the moon is doing, and grading it would cost the
    operator nights for a reason no passenger asked about.
    """
    rating, why = "good", []

    def bump(level, note):
        nonlocal rating
        if RANK[level] > RANK[rating]:
            rating = level
        why.append(note)

    rain = [r or 0.0 for r in (w.get("rain") or [])]
    hours = max(len(rain), 1) * (0.25 if w.get("resolution") == "15min" else 1.0)
    mmph = sum(rain) / hours if rain else 0.0
    if mmph >= t["rain_poor_mm_per_hour"]:
        bump("poor", f"rain {mmph:.1f} mm/h, too wet to run")
    elif mmph >= t["rain_marginal_mm_per_hour"]:
        bump("marginal", f"rain {mmph:.1f} mm/h, passengers will feel it")

    gusts = [g for g in (w.get("wind_gusts_10m") or []) if g is not None]
    gmax = max(gusts) if gusts else 0.0
    if gmax >= t["gust_poor_kmh"]:
        bump("poor", f"gusts {gmax:.0f} km/h, the boat will not hold position")
    elif gmax >= t["gust_marginal_kmh"]:
        bump("marginal", f"gusts {gmax:.0f} km/h")

    codes = [c for c in (w.get("weather_code") or []) if c is not None]
    if any(c in C.HAZARD["thunder_codes"] for c in codes):
        bump("poor", "thunderstorm in the window")

    # Reported, not rated.
    note = (f"moon {moon_pct} percent, a thinner display than on a dark night"
            if moon_pct > t["moon_marginal_max_pct"]
            else f"moon {moon_pct} percent, a dark sky and the best display"
            if moon_pct <= t["moon_good_max_pct"]
            else f"moon {moon_pct} percent")

    return {"rating": rating, "why": why or ["clear and calm"], "moon_pct": moon_pct,
            "moon_note": note, "max_gust_kmh": round(gmax, 1),
            "rain_mm_per_hour": round(mmph, 2)}


def score_combined(day: dict, trip_id: str = "sunset_firefly") -> dict:
    trip = C.COMBINED_TRIPS[trip_id]
    phases = phase_windows(day, trip)
    on = datetime.strptime(day["date"], "%Y-%m-%d").date()
    moon_pct = M.illumination_pct(on)

    scored = {}
    for ph in phases:
        w = F.slice_window(day, ph["start"], ph["end"])
        if ph["id"] == "sunset":
            r = _sunset_note(w, ph["thresholds"])
            r["rating"] = None            # a note has no rating, by design
        else:
            r = _score_firefly(w, ph["thresholds"], moon_pct)
        r.update({"label": ph["label"], "window": f"{ph['start']} to {ph['end']}",
                  "minutes": ph["minutes"]})
        scored[ph["id"]] = r

    prim = scored["firefly"]
    sun = scored["sunset"]

    # The rating is the passage decision and nothing else.
    overall = prim["rating"]
    prim["counts_toward_rating"] = True
    sun["counts_toward_rating"] = False

    short = prim["minutes"] < trip["min_firefly_minutes"]

    if overall == "poor":
        sell = "Do not run. " + prim["why"][0] + "."
    elif overall == "marginal":
        sell = "Runnable. " + prim["why"][0].capitalize() + "."
    else:
        sell = "Good night for it. Clear and calm on the river."

    guest = [sun["say"], prim["moon_note"].capitalize() + "."]

    if short:
        sell += (f" Only {prim['minutes']} minutes of firefly time fits before 21:00, "
                 f"under the {trip['min_firefly_minutes']} minute mark.")

    return {
        "trip": trip["name"], "slot": trip["slot"], "date": day["date"],
        "sunset_time": day["daily"]["sunset"][11:],
        "overall": overall, "rated_on": "passage: rain, wind, thunderstorm",
        "bonus": {"state": sun["state"], "say": sun["say"]},
        "tell_the_guest": guest,
        "phases": scored, "recommendation": sell,
        "moon_pct": moon_pct, "moon_phase": M.phase_name(on),
        "disclaimer": C.DISCLAIMER,
    }


if __name__ == "__main__":
    print("EVENING FIREFLY RUN, 19:00 to 21:00")
    print()
    hdr = ("date        RATING    rated on     moon  cloud   sunset      "
           "what you tell the guest")
    print(hdr)
    print("-" * 122)
    for d in range(21, 29):
        day = F.get_day(date(2026, 8, d))
        r = score_combined(day)
        s = r["phases"]["sunset"]
        cloud = str(s["avg_cloud_pct"] or "-")
        row = (r["date"].ljust(12) + r["overall"].upper().ljust(10)
               + "fireflies".ljust(13) + (str(r["moon_pct"]) + "%").rjust(5)
               + cloud.rjust(7) + "   " + r["bonus"]["state"].ljust(12)
               + r["recommendation"][:52])
        print(row)
    print()
    day = F.get_day(date(2026, 8, 24))
    r = score_combined(day)
    print("--- " + r["date"] + " in full, sunset " + r["sunset_time"] + " ---")
    for pid in ("firefly", "sunset"):
        ph = r["phases"][pid]
        tag = "SETS THE RATING" if ph.get("counts_toward_rating") else "bonus only, cannot downgrade"
        print("  " + ph["label"].ljust(14) + ph["window"] + "  (" + str(ph["minutes"])
              + " min)  " + ph["rating"].ljust(9) + " [" + tag + "]")
        for w in ph["why"]:
            print("      " + w)
    print()
    print("  RATING: " + r["overall"].upper())
    print("  You:    " + r["recommendation"])
    print("  Guest:  " + r["bonus"]["say"])
