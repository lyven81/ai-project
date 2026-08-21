"""
Stage B: how far ahead is a departure worth promising?

This is the measurement behind the booking policy. Until it runs, the
confidence tiers in config.py are an estimate written by hand. After it runs,
they are this location's own record.

Method. Open-Meteo's previous-runs endpoint returns, for the same timestamps,
what actually happened and what the forecast said 1, 3, 5 and 7 days earlier.
So for every past departure we can ask: did the forecast issued N days out
call this slot the way the day turned out?

Two error types, reported separately and never blended, because they do not
cost the same:

  said workable, turned out not     the boat sails and the trip is spoiled
  said not workable, turned out fine   a fare is refused for nothing

A single accuracy figure would hide the first inside the second.

Scope note. Only rain and gusts have previous-run variants, so the rating used
here is the rain-and-wind core of the full rating. Probability and visibility
are excluded, which makes this a slightly conservative read rather than an
optimistic one.

Run:  python eval_stage_b.py
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import config as C
import brain as B

RESULTS = Path(__file__).resolve().parent.parent / "results"
PREV_URL = "https://previous-runs-api.open-meteo.com/v1/forecast"
LEADS = [1, 3, 5, 7]
PAST_DAYS = 92


def fetch() -> dict:
    hourly = ["precipitation", "wind_gusts_10m"]
    for n in LEADS:
        hourly += [f"precipitation_previous_day{n}", f"wind_gusts_10m_previous_day{n}"]
    params = {
        "latitude": C.LOCATION["latitude"], "longitude": C.LOCATION["longitude"],
        "timezone": C.LOCATION["timezone"], "hourly": ",".join(hourly),
        "past_days": PAST_DAYS, "forecast_days": 1,
    }
    url = PREV_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def _mins(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def window(h: dict, day: str, start: str, end: str, rain_key: str, gust_key: str):
    s, e = _mins(start), _mins(end)
    idx = [i for i, t in enumerate(h["time"])
           if t.startswith(day) and s <= _mins(t[11:16]) < e]
    if not idx:
        return None
    rain = [h[rain_key][i] for i in idx]
    gust = [h[gust_key][i] for i in idx]
    if any(x is None for x in rain) or any(x is None for x in gust):
        return None
    return {"rain": rain, "wind_gusts_10m": gust,
            "time": [h["time"][i] for i in idx], "resolution": "hourly"}


def core_rating(w: dict) -> str:
    """The rain-and-wind half of the full rating, which is what is measurable
    at every lead time."""
    t = C.THRESHOLDS["sheltered"]
    gust = max(w["wind_gusts_10m"])
    mmph = sum(w["rain"]) / 2.0
    if gust >= t["gust_poor_kmh"] or mmph >= t["rain_poor_mm_per_hour"]:
        return "poor"
    if gust >= t["gust_marginal_kmh"] or mmph > 0:
        return "marginal"
    return "good"


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("=" * 72)
    print("STAGE B  forecast skill by lead time, Kuala Sepetang")
    print("=" * 72)
    print(f"\npulling {PAST_DAYS} days of analysis plus previous runs at leads {LEADS} ...")

    raw = fetch()
    h = raw["hourly"]
    all_days = sorted({t[:10] for t in h["time"]})
    print(f"{len(all_days)} dates, {len(C.SLOTS)} departures each\n")

    per_lead = {}
    for lead in LEADS:
        rk, gk = f"precipitation_previous_day{lead}", f"wind_gusts_10m_previous_day{lead}"
        n = shape_hit = rate_hit = wetdry_hit = 0
        sail_spoiled = 0      # said workable, turned out poor
        refused_fine = 0      # said poor, turned out workable
        said_workable = said_poor = 0
        wet_truth = 0

        for day in all_days:
            for slot in C.SLOTS:
                tw = window(h, day, slot["start"], slot["end"], "precipitation", "wind_gusts_10m")
                fw = window(h, day, slot["start"], slot["end"], rk, gk)
                if not tw or not fw:
                    continue
                n += 1
                ts = B.classify_shape(tw)["shape"]
                fs = B.classify_shape(fw)["shape"]
                # The coarser question the operator can actually act on far out:
                # will this departure have rain in it at all?
                if (ts == "dry") == (fs == "dry"):
                    wetdry_hit += 1
                tr, fr = core_rating(tw), core_rating(fw)
                if ts == fs:
                    shape_hit += 1
                if tr == fr:
                    rate_hit += 1
                if ts != "dry":
                    wet_truth += 1
                if fr != "poor":
                    said_workable += 1
                    if tr == "poor":
                        sail_spoiled += 1
                else:
                    said_poor += 1
                    if tr != "poor":
                        refused_fine += 1

        per_lead[lead] = {
            "slot_days": n,
            "wet_dry_agreement_pct": round(100 * wetdry_hit / n, 1) if n else None,
            "shape_agreement_pct": round(100 * shape_hit / n, 1) if n else None,
            "rating_agreement_pct": round(100 * rate_hit / n, 1) if n else None,
            "said_workable": said_workable,
            "sailed_and_spoiled": sail_spoiled,
            "sailed_and_spoiled_pct": round(100 * sail_spoiled / said_workable, 1) if said_workable else None,
            "said_poor": said_poor,
            "refused_for_nothing": refused_fine,
            "refused_for_nothing_pct": round(100 * refused_fine / said_poor, 1) if said_poor else None,
            "wet_slot_days_pct": round(100 * wet_truth / n, 1) if n else None,
        }

    # A baseline the forecast has to beat: always say the commonest outcome.
    # Without it, 50 percent agreement is uninterpretable.
    truth_shapes, truth_wet = {}, 0
    total = 0
    for day in all_days:
        for slot in C.SLOTS:
            tw = window(h, day, slot["start"], slot["end"], "precipitation", "wind_gusts_10m")
            if not tw:
                continue
            total += 1
            ts = B.classify_shape(tw)["shape"]
            truth_shapes[ts] = truth_shapes.get(ts, 0) + 1
            if ts != "dry":
                truth_wet += 1
    base_shape = round(100 * max(truth_shapes.values()) / total, 1)
    base_wetdry = round(100 * max(truth_wet, total - truth_wet) / total, 1)

    def skill(acc, base):
        if acc is None or base >= 100:
            return None
        return round((acc - base) / (100 - base), 3)

    for lead in LEADS:
        r = per_lead[lead]
        r["skill_vs_baseline_shape"] = skill(r["shape_agreement_pct"], base_shape)
        r["skill_vs_baseline_wetdry"] = skill(r["wet_dry_agreement_pct"], base_wetdry)
        r["small_sample_warning"] = r["said_poor"] < 30

    print(f"\nbaselines   always-say-commonest: shape {base_shape}%, wet-or-dry {base_wetdry}%")
    print(f"truth mix   {truth_shapes}\n")

    print(f"{'lead':>5} {'slot-days':>10} {'shape':>8} {'skill':>7} {'wet/dry':>9} {'skill':>7} "
          f"{'sailed+spoiled':>16}")
    print("-" * 78)
    for lead in LEADS:
        r = per_lead[lead]
        print(f"{lead:>4}d {r['slot_days']:>10} {r['shape_agreement_pct']:>7}% "
              f"{r['skill_vs_baseline_shape']:>7} "
              f"{r['wet_dry_agreement_pct']:>8}% {r['skill_vs_baseline_wetdry']:>7} "
              f"{str(r['sailed_and_spoiled']) + '/' + str(r['said_workable']):>11} "
              f"{str(r['sailed_and_spoiled_pct']) + '%':>6}")

    # Where does it stop being decision grade? The costly error is the one that
    # sets the line, not overall agreement.
    # The tier is set by skill over the baseline, not by raw agreement. A
    # forecast that only matches "always say dry" has told the operator nothing
    # they did not already know about this coast.
    def tier_for(lead: int) -> str:
        r = per_lead[lead]
        sh = r["skill_vs_baseline_shape"] or 0
        wd = r["skill_vs_baseline_wetdry"] or 0
        if sh >= 0.30 and wd >= 0.30:
            return "firm"
        if sh >= 0.15 or wd >= 0.25:
            return "indicative"
        if wd >= 0.05:
            return "provisional"
        return "pattern"

    measured = {lead: tier_for(lead) for lead in LEADS}
    print("\nmeasured tier by lead:", ", ".join(f"{k}d {v}" for k, v in measured.items()))

    verdict = []
    for lead in LEADS:
        r = per_lead[lead]
        verdict.append(
            f"At {lead} day{'s' if lead > 1 else ''} out: gets wet-or-dry right "
            f"{r['wet_dry_agreement_pct']}% of departures (baseline {base_wetdry}%, "
            f"skill {r['skill_vs_baseline_wetdry']}), and the exact rain shape "
            f"{r['shape_agreement_pct']}% (baseline {base_shape}%, skill "
            f"{r['skill_vs_baseline_shape']})."
        )
    for line in verdict:
        print("  " + line)

    out = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "location": C.LOCATION["name"],
        "window_days": len(all_days),
        "leads": LEADS,
        "baselines": {"shape_pct": base_shape, "wet_or_dry_pct": base_wetdry,
                      "truth_shape_mix": truth_shapes},
        "per_lead": per_lead,
        "measured_tier_by_lead": measured,
        "plain_language": verdict,
        "scope_note": "Rating here is the rain-and-wind core. Probability and "
                      "visibility have no previous-run variants, so they are "
                      "excluded, making this a conservative read.",
        "how_to_read": "The costly error is 'sailed and spoiled': the app said a "
                       "departure was workable and it was not. That is the number "
                       "that sets how far ahead a slot can be promised. "
                       "'Refused for nothing' costs one fare and is the cheaper miss.",
    }
    (RESULTS / "stage-b-horizon.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nsaved -> results/stage-b-horizon.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
