"""
Moon illumination, computed locally. No API call.

Open-Meteo does not return moon phase, but two of the twelve activities need
it: stargazing competes with moonlight, and firefly displays read best on a
dark night. A synodic-month approximation is accurate to a few percent, which
is far finer than the decision needs.
"""

from datetime import date, datetime

# Mean synodic month, in days.
SYNODIC = 29.530588853

# A known new moon, used as the reference epoch: 6 January 2000, 18:14 UTC.
_EPOCH = datetime(2000, 1, 6, 18, 14)


def moon_age_days(on: date) -> float:
    """Days since the last new moon, 0 to 29.53."""
    when = datetime(on.year, on.month, on.day, 12, 0)
    elapsed = (when - _EPOCH).total_seconds() / 86400.0
    return elapsed % SYNODIC


def illumination_pct(on: date) -> int:
    """
    Illuminated share of the disc, 0 to 100.

    0 is new moon, 100 is full. The curve is the standard cosine of the phase
    angle, so the number moves the way the sky does rather than linearly.
    """
    age = moon_age_days(on)
    phase_angle = 2.0 * 3.141592653589793 * age / SYNODIC
    # cos runs +1 at new moon to -1 at full; map to 0..1 illuminated.
    import math
    frac = (1.0 - math.cos(phase_angle)) / 2.0
    return int(round(frac * 100))


def phase_name(on: date) -> str:
    """Plain-language phase, for the operator rather than for an almanac."""
    age = moon_age_days(on)
    if age < 1.85:
        return "new moon"
    if age < 5.5:
        return "waxing crescent"
    if age < 9.2:
        return "first quarter"
    if age < 12.9:
        return "waxing gibbous"
    if age < 16.6:
        return "full moon"
    if age < 20.3:
        return "waning gibbous"
    if age < 24.0:
        return "last quarter"
    if age < 27.7:
        return "waning crescent"
    return "new moon"


def describe(on: date) -> dict:
    pct = illumination_pct(on)
    return {
        "date": on.isoformat(),
        "illumination_pct": pct,
        "phase": phase_name(on),
        "dark_sky": pct <= 40,
    }


if __name__ == "__main__":
    # Spot check against known 2026 phases.
    for d in ["2026-01-03", "2026-01-18", "2026-08-21", "2026-08-28", "2026-09-11"]:
        y, m, dd = (int(x) for x in d.split("-"))
        print(d, describe(date(y, m, dd)))
