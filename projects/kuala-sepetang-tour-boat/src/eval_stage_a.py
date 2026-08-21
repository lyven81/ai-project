"""
Stage A: prove the classifier before any language model is involved.

This is the hard gate. Nothing above it calls an LLM, so a failure here is a
failure of the rules, which is exactly what should be fixed first. If the
classifier cannot separate rain that clears from rain that arrives on a day
the operator remembers, the app is not ready for a chat interface.

Three checks, in order of strictness:

  1. Planted shapes    hand-built windows whose shape is known by construction,
                       including the edge cases that decide the boundaries
  2. Properties        invariants that must hold on real archive data,
                       whatever the weather did
  3. Distribution      do all five shapes actually occur over a season, and
                       does the rating spread look like a usable day rather
                       than everything red or everything green

Run:  python eval_stage_a.py
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import config as C
import brain as B
import forecast as F

RESULTS = Path(__file__).resolve().parent.parent / "results"
ARCHIVE_DAYS = 120          # one API call, not 120
WET = C.WET_BUCKET_MM


# ---------------------------------------------------------------------------
# 1. Planted shapes. Known by construction.
# ---------------------------------------------------------------------------

def _w(rain, times=None):
    """A minimal window payload carrying just what classify_shape reads."""
    n = len(rain)
    times = times or [f"2026-01-01T15:{15*i:02d}" if i < 4 else
                      f"2026-01-01T16:{15*(i-4):02d}" for i in range(n)]
    return {"rain": rain, "time": times, "resolution": "15min"}


PLANTED = [
    # name,                       rain per 15-min bucket,                expected
    ("all dry",                   [0, 0, 0, 0, 0, 0, 0, 0],              "dry"),
    ("trace below threshold",     [0.05, 0.05, 0, 0, 0, 0, 0, 0],        "dry"),
    ("exactly at threshold",      [WET, 0, 0, 0, 0, 0, 0, 0],            "clears"),
    ("wet end to end",            [1, 1, 1, 1, 1, 1, 1, 1],              "throughout"),
    ("six of eight wet",          [1, 1, 1, 1, 1, 1, 0, 0],              "throughout"),
    ("five of eight, front",      [1, 1, 1, 1, 1, 0, 0, 0],              "intermittent"),
    ("first bucket only",         [2, 0, 0, 0, 0, 0, 0, 0],              "clears"),
    ("front half only",           [1, 1, 1, 0, 0, 0, 0, 0],              "clears"),
    ("last bucket only",          [0, 0, 0, 0, 0, 0, 0, 2],              "arrives"),
    ("back half only",            [0, 0, 0, 0, 1, 1, 1, 0],              "arrives"),
    ("straddles the midpoint",    [0, 0, 0, 1, 1, 0, 0, 0],              "intermittent"),
    ("alternating showers",       [1, 0, 1, 0, 1, 0, 0, 0],              "intermittent"),
    # hourly resolution, which is what the archive returns
    ("hourly: dry",               [0, 0],                                 "dry"),
    ("hourly: first hour wet",    [1, 0],                                 "clears"),
    ("hourly: second hour wet",   [0, 1],                                 "arrives"),
    ("hourly: both wet",          [1, 1],                                 "throughout"),
]


def check_planted() -> tuple[int, int, list]:
    failures = []
    for name, rain, expected in PLANTED:
        got = B.classify_shape(_w(rain))["shape"]
        if got != expected:
            failures.append({"case": name, "rain": rain,
                             "expected": expected, "got": got})
    return len(PLANTED) - len(failures), len(PLANTED), failures


# ---------------------------------------------------------------------------
# 2. Properties on real archive data
# ---------------------------------------------------------------------------

def fetch_archive_range(start: date, end: date) -> dict:
    params = {
        "latitude": C.LOCATION["latitude"], "longitude": C.LOCATION["longitude"],
        "timezone": C.LOCATION["timezone"],
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "hourly": "precipitation,rain,wind_gusts_10m,cloud_cover,visibility,weather_code,temperature_2m",
        "daily": "sunrise,sunset,precipitation_sum,wind_gusts_10m_max",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def _day_from_range(raw: dict, day_str: str) -> dict:
    """Carve one date out of a multi-day archive pull, in get_day() shape."""
    h = raw["hourly"]
    idx = [i for i, t in enumerate(h["time"]) if t.startswith(day_str)]
    hourly = {"time": [h["time"][i] for i in idx]}
    for k, v in h.items():
        if k != "time":
            hourly[k] = [v[i] for i in idx]
    d = raw["daily"]
    di = d["time"].index(day_str)
    return {
        "date": day_str, "source": "archive", "lead_days": 0,
        "hourly": hourly, "minutely_15": {}, "has_minutely": False,
        "daily": {"sunrise": d["sunrise"][di], "sunset": d["sunset"][di],
                  "precipitation_sum": d["precipitation_sum"][di],
                  "wind_gusts_10m_max": d["wind_gusts_10m_max"][di]},
    }


def check_properties(days: list[dict]) -> tuple[int, int, list]:
    """
    Invariants that must hold whatever the weather did.

    These are not a restatement of the classifier. Each one could fail if the
    boundary logic were wrong, and each says something the operator relies on.
    """
    violations, checked = [], 0

    for day in days:
        for slot in C.SLOTS:
            try:
                w = F.slice_window(day, slot["start"], slot["end"])
            except F.ForecastError:
                continue
            s = B.classify_shape(w)
            rain = [r or 0.0 for r in (w.get("rain") or [])]
            wet = [r >= WET for r in rain]
            n = len(wet)
            if n < 2:
                continue
            half = n // 2
            checked += 1
            tag = f"{day['date']} {slot['id']}"

            # P1: no measurable rain means the shape must be dry.
            if sum(wet) == 0 and s["shape"] != "dry":
                violations.append({"prop": "P1 no rain implies dry", "at": tag, "got": s["shape"]})

            # P2: every bucket wet means the shape must be throughout.
            if all(wet) and s["shape"] != "throughout":
                violations.append({"prop": "P2 all wet implies throughout", "at": tag, "got": s["shape"]})

            # P3: "clears" requires the last wet bucket in the first half.
            if s["shape"] == "clears":
                last = max(i for i, x in enumerate(wet) if x)
                if last >= half:
                    violations.append({"prop": "P3 clears has late rain", "at": tag, "last_wet": last, "half": half})

            # P4: "arrives" requires the first wet bucket in the second half.
            if s["shape"] == "arrives":
                first = min(i for i, x in enumerate(wet) if x)
                if first < half:
                    violations.append({"prop": "P4 arrives has early rain", "at": tag, "first_wet": first, "half": half})

            # P5: the shape must be one of the five declared in config.
            if s["shape"] not in C.SHAPES:
                violations.append({"prop": "P5 unknown shape", "at": tag, "got": s["shape"]})

            # P6: a contingency line must exist for every shape produced.
            if not s.get("contingency"):
                violations.append({"prop": "P6 no contingency", "at": tag, "got": s["shape"]})

            # P7: the late-rain penalty must fire exactly when it should, in
            #     both directions. Rain arriving on the return leg costs a step
            #     once there is enough of it; a trace must cost nothing. Testing
            #     only one direction would let the penalty quietly apply to
            #     every drizzle, which is the fault this property now guards.
            v = B.score_slot(day, slot["id"], "sheltered")
            if v["shape"]["shape"] == "arrives" and v["comfort"]["rating"] != "poor":
                late = B._second_half_mm(w)
                penalised = B.RANK[v["rating"]] > B.RANK[v["comfort"]["rating"]]
                if late >= C.ARRIVES_PENALTY_MIN_MM and not penalised:
                    violations.append({"prop": "P7a real late rain not penalised", "at": tag,
                                       "late_mm": late, "rating": v["rating"],
                                       "comfort": v["comfort"]["rating"]})
                if late < C.ARRIVES_PENALTY_MIN_MM and penalised:
                    violations.append({"prop": "P7b trace penalised", "at": tag,
                                       "late_mm": late, "rating": v["rating"],
                                       "comfort": v["comfort"]["rating"]})

            # P8: a hazard stop must always produce a poor rating.
            if v["hazard"]["stop"] and v["rating"] != "poor":
                violations.append({"prop": "P8 hazard did not force poor", "at": tag, "rating": v["rating"]})

    return checked - len(violations), checked, violations


def check_monotonicity() -> tuple[int, int, list]:
    """More rain must never improve a rating. Tested by escalation."""
    failures, cases = [], 0
    base = [0.0] * 8
    prev = None
    for step in [0.0, 0.2, 0.5, 1.0, 2.0, 4.0, 8.0]:
        w = _w([step] * 8)
        r = B.rate_comfort(w, "sheltered")["rating"]
        cases += 1
        if prev is not None and B.RANK[r] < B.RANK[prev]:
            failures.append({"step_mm": step, "rating": r, "previous": prev})
        prev = r
    return cases - len(failures), cases, failures


def prove_hourly_reachability() -> dict:
    """
    Enumerate every wet pattern possible at hourly resolution.

    A two-hour departure read from hourly data has exactly two buckets, so
    there are four possible patterns. This walks all four and records which
    shapes can and cannot arise. It turns "intermittent never appeared" from
    an unexplained gap into a proven structural fact: intermittent needs wet
    buckets in both halves without filling three quarters of them, which two
    buckets cannot express.

    The live app reads 15-minute data, where all five shapes are reachable and
    the planted cases prove it.
    """
    seen = {}
    for a in (0.0, 1.0):
        for b in (0.0, 1.0):
            shape = B.classify_shape(_w([a, b], times=["T15:00", "T16:00"]))["shape"]
            seen.setdefault(shape, []).append([a, b])
    reachable = sorted(seen)
    unreachable = sorted(set(C.SHAPES) - set(seen))
    return {
        "patterns_enumerated": 4,
        "reachable_at_hourly": reachable,
        "unreachable_at_hourly": unreachable,
        "proof": "All 2^2 hourly patterns walked. Shapes not listed cannot arise "
                 "at this resolution by construction, not by absence of weather.",
    }


# ---------------------------------------------------------------------------
# 3. Distribution
# ---------------------------------------------------------------------------

def check_distribution(days: list[dict]) -> dict:
    shapes, ratings = {}, {}
    for day in days:
        for slot in C.SLOTS:
            try:
                v = B.score_slot(day, slot["id"], "sheltered")
            except F.ForecastError:
                continue
            shapes[v["shape"]["shape"]] = shapes.get(v["shape"]["shape"], 0) + 1
            ratings[v["rating"]] = ratings.get(v["rating"], 0) + 1
    total = sum(shapes.values()) or 1
    return {
        "slot_days": total,
        "shapes": shapes,
        "shape_pct": {k: round(100 * v / total, 1) for k, v in shapes.items()},
        "ratings": ratings,
        "rating_pct": {k: round(100 * v / total, 1) for k, v in ratings.items()},
        "all_five_shapes_seen": set(shapes) == set(C.SHAPES),
        "missing_shapes": sorted(set(C.SHAPES) - set(shapes)),
    }


# ---------------------------------------------------------------------------

def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("=" * 68)
    print("STAGE A  classifier check, no language model involved")
    print("=" * 68)

    p_pass, p_total, p_fail = check_planted()
    print(f"\n1. Planted shapes      {p_pass}/{p_total} passed")
    for f in p_fail:
        print(f"   FAIL {f['case']:<26} expected {f['expected']:<13} got {f['got']}")

    m_pass, m_total, m_fail = check_monotonicity()
    print(f"\n2. Monotonicity        {m_pass}/{m_total} passed")
    for f in m_fail:
        print(f"   FAIL rating improved as rain rose: {f}")

    end = date.today() - timedelta(days=7)
    start = end - timedelta(days=ARCHIVE_DAYS)
    print(f"\n3. Real archive        {start} to {end}, one call")
    raw = fetch_archive_range(start, end)
    days = [_day_from_range(raw, d) for d in raw["daily"]["time"]]
    print(f"   {len(days)} days pulled")

    r_pass, r_total, r_viol = check_properties(days)
    print(f"\n4. Properties          {r_pass}/{r_total} slot-days passed 8 invariants")
    for v in r_viol[:12]:
        print(f"   VIOLATION {v}")
    if len(r_viol) > 12:
        print(f"   ... and {len(r_viol) - 12} more")

    reach = prove_hourly_reachability()
    print(f"\n5. Reachability        all {reach['patterns_enumerated']} hourly patterns enumerated")
    print(f"   reachable at hourly    {reach['reachable_at_hourly']}")
    print(f"   unreachable at hourly  {reach['unreachable_at_hourly']}  (proven, not missing)")

    dist = check_distribution(days)
    print(f"\n6. Distribution        {dist['slot_days']} slot-days of real weather")
    print(f"   shapes   {dist['shape_pct']}")
    print(f"   ratings  {dist['rating_pct']}")

    expected = set(reach["reachable_at_hourly"])
    missing = sorted(expected - set(dist["shapes"]))
    if missing:
        print(f"   NOT SEEN {missing}  <- reachable but never fired, so a real dead branch")
    else:
        print("   every hourly-reachable shape fired on real data")

    # Five-shape coverage is proven at 15-minute resolution by the planted
    # cases, which is the resolution the live app actually runs at.
    planted_shapes = {exp for _, _, exp in PLANTED}
    five_covered = planted_shapes >= set(C.SHAPES)
    print(f"   all five shapes covered by planted cases: {five_covered}")

    ok = (not p_fail) and (not m_fail) and (not r_viol) and (not missing) and five_covered
    print("\n" + "=" * 68)
    print("GATE:", "PASS" if ok else "FAIL")
    print("=" * 68)

    out = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": len(days)},
        "planted": {"passed": p_pass, "total": p_total, "failures": p_fail},
        "monotonicity": {"passed": m_pass, "total": m_total, "failures": m_fail},
        "properties": {"passed": r_pass, "total": r_total, "violations": r_viol},
        "reachability": reach,
        "distribution": dist,
        "five_shapes_covered_by_planted_cases": five_covered,
        "gate": "PASS" if ok else "FAIL",
        "note": "Archive data is hourly, so real-data windows carry 2 buckets and "
                "only four of the five shapes can arise. The live forecast carries "
                "8 buckets per slot, where all five are reachable and the planted "
                "cases prove it. One consequence to watch: at hourly resolution a "
                "light drizzle in both hours reads as 'throughout', which is why "
                "that share looks high here and would fall at 15-minute resolution.",
    }
    (RESULTS / "stage-a.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved -> results/stage-a.json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
