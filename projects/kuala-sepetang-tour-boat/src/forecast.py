"""
Forecast layer: one cached Open-Meteo call per date.

Three endpoints, all free and keyless:

  forecast              what is predicted from now out to 16 days
  archive               what actually happened on a past date
  historical-forecast   what was predicted for a past date, before it happened

The third is what makes the recovery check possible: predicted and observed
both exist for thousands of past slots, so the classifier can be scored
without waiting for new weather.

Everything is pinned to Asia/Kuala_Lumpur. The API defaults to GMT, and an
eight-hour offset would move every departure without looking broken.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

from config import LOCATION

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HISTORICAL_FORECAST_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

HOURLY_VARS = [
    "precipitation_probability", "precipitation", "rain",
    "wind_speed_10m", "wind_gusts_10m", "cloud_cover", "visibility",
    "weather_code", "is_day", "temperature_2m", "cape",
]

# Verified present at 4.84N 100.63E on 21 Aug 2026: 192 non-null buckets
# over two days, so a two-hour slot gets eight buckets instead of two.
MINUTELY_VARS = ["precipitation", "rain", "wind_gusts_10m", "weather_code"]

DAILY_VARS = ["sunrise", "sunset", "precipitation_sum", "wind_gusts_10m_max"]


class ForecastError(RuntimeError):
    """Raised with a message the model can read and act on."""


# ---------------------------------------------------------------------------
# Cache. TTL scales with lead time: tomorrow's forecast is worth refreshing
# often, day twelve is not going to move in the next hour.
# ---------------------------------------------------------------------------

def _ttl_seconds(target: date) -> int:
    lead = (target - date.today()).days
    if lead <= 0:
        return 15 * 60
    if lead == 1:
        return 30 * 60
    if lead <= 3:
        return 3 * 60 * 60
    return 12 * 60 * 60


def _cache_path(kind: str, target: date) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{kind}_{target.isoformat()}.json"


def _read_cache(kind: str, target: date):
    p = _cache_path(kind, target)
    if not p.exists():
        return None
    # The archive never changes, so it never expires.
    if kind != "archive" and time.time() - p.stat().st_mtime > _ttl_seconds(target):
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(kind: str, target: date, payload: dict) -> None:
    _cache_path(kind, target).write_text(
        json.dumps(payload), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _get(url: str, params: dict, retries: int = 3) -> dict:
    query = urllib.parse.urlencode(params, doseq=True)
    full = f"{url}?{query}"
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(full, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:                     # noqa: BLE001
            last = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise ForecastError(
        f"Could not reach the weather service after {retries} tries: {last}. "
        f"Try again in a moment."
    )


def _base_params() -> dict:
    return {
        "latitude": LOCATION["latitude"],
        "longitude": LOCATION["longitude"],
        "timezone": LOCATION["timezone"],
    }


# ---------------------------------------------------------------------------
# Public: one call per date, cached
# ---------------------------------------------------------------------------

MAX_LEAD_DAYS = 15   # the API serves 16 days counting today


def parse_date(value: str) -> date:
    """
    Accept an ISO date, or the words today and tomorrow.

    Raises with a message the model can correct itself from.
    """
    if not value:
        raise ForecastError("A date is required, in YYYY-MM-DD form.")
    v = value.strip().lower()
    if v == "today":
        return date.today()
    if v == "tomorrow":
        return date.today() + timedelta(days=1)
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        raise ForecastError(
            f"Could not read '{value}' as a date. Use YYYY-MM-DD, "
            f"for example {date.today().isoformat()}, or the word today or tomorrow."
        ) from None


def lead_days(target: date) -> int:
    return (target - date.today()).days


def get_day(target: date, allow_past: bool = False) -> dict:
    """
    Everything known about one date at Kuala Sepetang, in one payload.

    Past dates come from the archive, future dates from the forecast. Both
    return the same shape so nothing downstream has to care which it got.

    `allow_past` defaults to False, and that default is the point.

    The archive and the forecast return identical shapes, which is convenient
    for the measurement code and dangerous everywhere else: a date the model
    guessed wrong lands in the archive and comes back as real weather, at zero
    days lead, labelled firm. Nothing in the payload says it already happened.
    That is how a question about "this Sunday" was answered with August 2024.

    So a past date is now an error by default, and the message carries today's
    date, because the caller that asked for a past date is usually a model that
    got its arithmetic wrong and can correct itself if it is told what day it
    is. The measurement code passes allow_past=True and gets the old behaviour.
    """
    lead = lead_days(target)

    if lead > MAX_LEAD_DAYS:
        raise ForecastError(
            f"{target.isoformat()} is {lead} days out. The forecast only reaches "
            f"{MAX_LEAD_DAYS} days ahead, to "
            f"{(date.today() + timedelta(days=MAX_LEAD_DAYS)).isoformat()}. "
            f"Nothing can be said about a specific departure that far out."
        )

    if lead < 0:
        if not allow_past:
            today = date.today()
            raise ForecastError(
                f"{target.isoformat()} ({target.strftime('%A')}) is {abs(lead)} "
                f"day{'s' if abs(lead) != 1 else ''} in the past. Weather for a past "
                f"date is what happened, not a forecast, so it cannot answer a "
                f"question about whether a departure should run. "
                f"Today is {today.isoformat()} ({today.strftime('%A')}). "
                f"If you meant an upcoming date, call get_current_datetime and work "
                f"it out from there rather than from memory."
            )
        return _get_archive(target)
    return _get_forecast(target)


def _get_forecast(target: date) -> dict:
    cached = _read_cache("forecast", target)
    if cached:
        return cached

    params = _base_params() | {
        "hourly": ",".join(HOURLY_VARS),
        "minutely_15": ",".join(MINUTELY_VARS),
        "daily": ",".join(DAILY_VARS),
        "start_date": target.isoformat(),
        "end_date": target.isoformat(),
    }
    raw = _get(FORECAST_URL, params)
    payload = _shape(raw, target, source="forecast")
    _write_cache("forecast", target, payload)
    return payload


def _get_archive(target: date) -> dict:
    cached = _read_cache("archive", target)
    if cached:
        return cached

    params = _base_params() | {
        "hourly": ",".join(v for v in HOURLY_VARS if v != "precipitation_probability"),
        "daily": ",".join(DAILY_VARS),
        "start_date": target.isoformat(),
        "end_date": target.isoformat(),
    }
    raw = _get(ARCHIVE_URL, params)
    payload = _shape(raw, target, source="archive")
    _write_cache("archive", target, payload)
    return payload


def get_past_forecast(target: date, issued_lead_days: int) -> dict:
    """
    What the forecast said for `target`, as issued `issued_lead_days` before it.

    Used only by the Stage B skill measurement. Not exposed as a chat tool.
    """
    params = _base_params() | {
        "hourly": ",".join(v for v in HOURLY_VARS if v != "cape"),
        "start_date": target.isoformat(),
        "end_date": target.isoformat(),
    }
    raw = _get(HISTORICAL_FORECAST_URL, params)
    payload = _shape(raw, target, source="historical_forecast")
    payload["issued_lead_days"] = issued_lead_days
    return payload


# ---------------------------------------------------------------------------
# Several dates in one call.
#
# The board asks for a week. Fetched a date at a time that was seven sequential
# HTTP calls, about sixteen seconds on a cold cache, and on Cloud Run with
# min-instances 0 the cache is cold every time an instance wakes. Open-Meteo
# serves the whole range in one request for the same data, so it does.
#
#   one call covering 7 days   2.0s
#   seven calls, one per day  12.3s
#
# Same payload, one sixth of the quota. The split writes every date into the
# cache, so get_day() for any of them is then free.
# ---------------------------------------------------------------------------

def _slice_block(block: dict, day_iso: str) -> dict:
    """The rows of an hourly or 15-minute block that belong to one date."""
    times = block.get("time") or []
    idx = [i for i, t in enumerate(times) if t[:10] == day_iso]
    if not idx:
        return {}
    out = {"time": [times[i] for i in idx]}
    for key, values in block.items():
        if key == "time" or not isinstance(values, list):
            continue
        out[key] = [values[i] if i < len(values) else None for i in idx]
    return out


def _split_range(raw: dict, targets: list[date], source: str) -> dict[date, dict]:
    """One multi-date response, cut into the per-date payloads everything
    downstream already expects."""
    hourly = raw.get("hourly") or {}
    minutely = raw.get("minutely_15") or {}
    daily = raw.get("daily") or {}
    daily_times = daily.get("time") or []

    out = {}
    for target in targets:
        iso = target.isoformat()
        h = _slice_block(hourly, iso)
        if not h.get("time"):
            continue                      # the API did not carry that date
        m = _slice_block(minutely, iso)

        di = daily_times.index(iso) if iso in daily_times else None

        def day_val(key):
            seq = daily.get(key) or []
            return seq[di] if di is not None and di < len(seq) else None

        out[target] = {
            "date": iso,
            "weekday": target.strftime("%A"),
            "source": source,
            "is_history": source == "archive",
            "lead_days": lead_days(target),
            "timezone": raw.get("timezone"),
            "utc_offset_seconds": raw.get("utc_offset_seconds"),
            "elevation_m": raw.get("elevation"),
            "hourly": h,
            "minutely_15": m,
            "has_minutely": bool(m.get("time")),
            "daily": {
                "sunrise": day_val("sunrise"),
                "sunset": day_val("sunset"),
                "precipitation_sum": day_val("precipitation_sum"),
                "wind_gusts_10m_max": day_val("wind_gusts_10m_max"),
            },
        }
    return out


def get_days(start: date, ndays: int) -> list[dict]:
    """
    Payloads for a run of consecutive dates, in order.

    Whatever is already cached is used. Anything missing is fetched in a single
    request spanning the gap, then cached, so a seven-day board costs one call
    rather than seven.
    """
    if ndays < 1:
        raise ForecastError("A board needs at least one day.")
    targets = [start + timedelta(days=i) for i in range(ndays)]

    last = targets[-1]
    if lead_days(last) > MAX_LEAD_DAYS:
        raise ForecastError(
            f"{last.isoformat()} is {lead_days(last)} days out. The forecast only "
            f"reaches {MAX_LEAD_DAYS} days ahead, to "
            f"{(date.today() + timedelta(days=MAX_LEAD_DAYS)).isoformat()}."
        )
    if lead_days(targets[0]) < 0:
        raise ForecastError(
            f"{targets[0].isoformat()} is in the past. Today is "
            f"{date.today().isoformat()}. A board starts today or later."
        )

    have = {t: _read_cache("forecast", t) for t in targets}
    missing = [t for t, v in have.items() if not v]

    if missing:
        lo, hi = min(missing), max(missing)
        params = _base_params() | {
            "hourly": ",".join(HOURLY_VARS),
            "minutely_15": ",".join(MINUTELY_VARS),
            "daily": ",".join(DAILY_VARS),
            "start_date": lo.isoformat(),
            "end_date": hi.isoformat(),
        }
        fetched = _split_range(_get(FORECAST_URL, params),
                              [lo + timedelta(days=i) for i in range((hi - lo).days + 1)],
                              source="forecast")
        for t, payload in fetched.items():
            _write_cache("forecast", t, payload)
            if t in have:
                have[t] = payload

    out = []
    for t in targets:
        if not have[t]:
            raise ForecastError(
                f"The weather service returned no data for {t.isoformat()}."
            )
        out.append(have[t])
    return out


def _shape(raw: dict, target: date, source: str) -> dict:
    """Normalise the three endpoints into one shape."""
    hourly = raw.get("hourly") or {}
    minutely = raw.get("minutely_15") or {}
    daily = raw.get("daily") or {}

    if not hourly.get("time"):
        raise ForecastError(
            f"The weather service returned no hourly data for {target.isoformat()}."
        )

    def first(seq, default=None):
        return seq[0] if seq else default

    return {
        "date": target.isoformat(),
        "weekday": target.strftime("%A"),
        "source": source,
        # Says so in the payload, not only in the variable name. Anything that
        # renders or reports this can tell observation from forecast without
        # knowing which endpoint it came from.
        "is_history": source == "archive",
        "lead_days": lead_days(target),
        "timezone": raw.get("timezone"),
        "utc_offset_seconds": raw.get("utc_offset_seconds"),
        "elevation_m": raw.get("elevation"),
        "hourly": hourly,
        "minutely_15": minutely,
        "has_minutely": bool(minutely.get("time")),
        "daily": {
            "sunrise": first(daily.get("sunrise", [])),
            "sunset": first(daily.get("sunset", [])),
            "precipitation_sum": first(daily.get("precipitation_sum", [])),
            "wind_gusts_10m_max": first(daily.get("wind_gusts_10m_max", [])),
        },
    }


# ---------------------------------------------------------------------------
# Slicing helpers used by the brain
# ---------------------------------------------------------------------------

def _minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def slice_window(day: dict, start: str, end: str) -> dict:
    """
    Pull the buckets that fall inside a window.

    Returns the finest resolution available: 15-minute buckets where the API
    carried them, hourly otherwise. `resolution` says which, so a caller can
    tell an eight-bucket read from a two-bucket one.
    """
    s, e = _minutes(start), _minutes(end)
    if e <= s:
        raise ForecastError(
            f"The window {start} to {end} ends before it starts. "
            f"A departure runs two hours, so 15:00 pairs with 17:00."
        )

    if day.get("has_minutely"):
        block = day["minutely_15"]
        resolution = "15min"
    else:
        block = day["hourly"]
        resolution = "hourly"

    times = block["time"]
    idx = [i for i, t in enumerate(times) if s <= _minutes(t[11:16]) < e]

    if not idx:
        raise ForecastError(
            f"No forecast data covers {start} to {end} on {day['date']}."
        )

    out = {"resolution": resolution, "time": [times[i] for i in idx]}
    for key, values in block.items():
        if key == "time":
            continue
        out[key] = [values[i] for i in idx]

    # Hourly variables the 15-minute block does not carry (probability, cloud,
    # visibility, cape) are always taken from the hourly series.
    hourly = day["hourly"]
    h_idx = [i for i, t in enumerate(hourly["time"]) if s <= _minutes(t[11:16]) < e]
    out["hourly_time"] = [hourly["time"][i] for i in h_idx]
    for key, values in hourly.items():
        if key == "time" or key in out:
            continue
        out[f"h_{key}"] = [values[i] for i in h_idx]

    return out


def hour_value(day: dict, hhmm: str, var: str):
    """One hourly value at one clock time, or None if the hour is not present."""
    hourly = day["hourly"]
    target = _minutes(hhmm)
    for i, t in enumerate(hourly["time"]):
        if _minutes(t[11:16]) == target:
            series = hourly.get(var) or []
            return series[i] if i < len(series) else None
    return None


if __name__ == "__main__":
    d = get_day(date.today())
    print("date:", d["date"], "| source:", d["source"], "| tz:", d["timezone"])
    print("minutely available:", d["has_minutely"])
    print("sunrise:", d["daily"]["sunrise"], "sunset:", d["daily"]["sunset"])
    w = slice_window(d, "15:00", "17:00")
    print("window resolution:", w["resolution"], "buckets:", len(w["time"]))
    print("rain:", w.get("rain"))
    print("gusts:", w.get("wind_gusts_10m"))
    print("prob (hourly):", w.get("h_precipitation_probability"))
