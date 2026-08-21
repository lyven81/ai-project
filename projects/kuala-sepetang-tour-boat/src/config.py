"""
Operator-owned configuration for Kuala Sepetang Tour Boat.

Everything in this file belongs to the boat operator, not to the model.
The numbers below are STARTING PLACEHOLDERS. They are wrong until the
operator corrects them from experience on the water.

Nothing here is a safety standard. The system reports conditions against
these thresholds. The operator on the water owns the go or no-go call.
"""

# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

LOCATION = {
    "name": "Kuala Sepetang",
    "state": "Perak",
    "latitude": 4.84,
    "longitude": 100.63,
    "timezone": "Asia/Kuala_Lumpur",
    # TODO(operator): confirm against the jetty itself, not the town centre.
    "coords_confirmed": False,
}

# ---------------------------------------------------------------------------
# The six fixed departures. One boat, two hours each, no overlap.
# ---------------------------------------------------------------------------

SLOTS = [
    {"id": "0900", "start": "09:00", "end": "11:00", "label": "09:00 to 11:00"},
    {"id": "1100", "start": "11:00", "end": "13:00", "label": "11:00 to 13:00"},
    {"id": "1300", "start": "13:00", "end": "15:00", "label": "13:00 to 15:00"},
    {"id": "1500", "start": "15:00", "end": "17:00", "label": "15:00 to 17:00"},
    {"id": "1700", "start": "17:00", "end": "19:00", "label": "17:00 to 19:00"},
    {"id": "1900", "start": "19:00", "end": "21:00", "label": "19:00 to 21:00"},
]

BOAT = {"name": "Boat 1", "seats": 12}

# The shortest notice on which a party can realistically be put on a different
# departure. A boat leaving in ten minutes is not somewhere you can move twelve
# people who are not at the jetty yet.
# TODO(operator): your call. Longer for school groups, shorter for walk-ins.
MIN_NOTICE_MINUTES = 60

# ---------------------------------------------------------------------------
# Thresholds. Split by exposure, because the open estuary and the sheltered
# mangrove channels do not behave the same in wind.
# ---------------------------------------------------------------------------

# A 15-minute bucket counts as wet at or above this many mm.
WET_BUCKET_MM = 0.1

# Share of buckets that must be wet before a slot is called wet throughout.
THROUGHOUT_SHARE = 0.75

# An activity needs this much of its own window inside a departure to be offered.
MIN_OVERLAP_MINUTES = 45

# Rain that arrives late is penalised, because the return leg is the exposed
# part of the trip. But a trace should not cost a slot: 0.3mm of drizzle in the
# last forty minutes is not a reason to cancel on a group of twelve. The
# penalty only applies once the late rain is worth putting a poncho on for.
# TODO(operator): this is the number most worth arguing with. What depth of
# rain in the second hour actually spoils a trip on your boat?
ARRIVES_PENALTY_MIN_MM = 0.5

THRESHOLDS = {
    "open": {          # estuary, dolphin runs, fishing, the long Kuala Sangga leg
        "gust_poor_kmh": 40,
        "gust_marginal_kmh": 25,
        "rain_poor_mm_per_hour": 2.0,
        "prob_poor_pct": 70,
        "prob_marginal_pct": 40,
        "visibility_poor_m": 2000,
    },
    "sheltered": {     # mangrove channels, fishing village, fish farm
        "gust_poor_kmh": 50,
        "gust_marginal_kmh": 32,
        "rain_poor_mm_per_hour": 3.0,
        "prob_poor_pct": 70,
        "prob_marginal_pct": 40,
        "visibility_poor_m": 1500,
    },
}

# Hazard is not a rating. It is a stop.
HAZARD = {
    # WMO weather codes for thunderstorm.
    "thunder_codes": {95, 96, 99},
    # Convective available potential energy. High values mean the atmosphere
    # is primed for storms even when no code has fired yet. Treated as a
    # heads-up, never as a stop on its own.
    "cape_watch_jkg": 2000,
    # Gusts at or above this are a stop regardless of exposure.
    "gust_stop_kmh": 55,
}

# ---------------------------------------------------------------------------
# The twelve activities. Windows marked "sunset" are computed per date.
# ---------------------------------------------------------------------------

ACTIVITIES = [
    {"id": "mangrove_cruise",  "name": "Mangrove river cruise",   "exposure": "sheltered",
     "window": ("clock", "09:00", "16:00"), "drivers": ["rain", "thunder"]},

    {"id": "fishing_village",  "name": "Fishing village tour",    "exposure": "sheltered",
     "window": ("clock", "09:00", "16:00"), "drivers": ["rain", "thunder"]},

    {"id": "mangrove_ecology", "name": "Mangrove ecology tour",   "exposure": "sheltered",
     "window": ("clock", "09:00", "16:00"), "drivers": ["rain", "thunder"]},

    {"id": "fish_farm",        "name": "Fish farm visit",         "exposure": "sheltered",
     "window": ("clock", "09:00", "16:00"), "drivers": ["rain"]},

    {"id": "eagle_watching",   "name": "Eagle watching",          "exposure": "sheltered",
     "window": ("clock", "15:00", "18:00"), "drivers": ["rain", "wind"]},

    {"id": "bird_watching",    "name": "Bird watching",           "exposure": "sheltered",
     "window": ("clock", "07:00", "10:00"), "drivers": ["rain", "wind"]},

    {"id": "dolphin",          "name": "Dolphin spotting",        "exposure": "open",
     "window": ("clock", "07:00", "11:00"), "drivers": ["wind", "rain", "visibility"]},

    {"id": "fishing_trip",     "name": "Fishing trip",            "exposure": "open",
     "window": ("clock", "07:00", "12:00"), "drivers": ["wind", "rain"]},

    {"id": "sunset_cruise",    "name": "Sunset cruise",           "exposure": "open",
     "window": ("sunset", -90, +20), "drivers": ["cloud_band", "rain", "wind"]},

    {"id": "firefly",          "name": "Firefly watching",        "exposure": "sheltered",
     "window": ("sunset", +30, +150), "drivers": ["rain", "wind", "moon"]},

    {"id": "stargazing",       "name": "Stargazing",              "exposure": "sheltered",
     "window": ("sunset", +90, +240), "drivers": ["cloud", "moon", "rain"]},

    {"id": "kuala_sangga",     "name": "Kuala Sangga village",    "exposure": "open",
     "window": ("clock", "09:00", "15:00"), "drivers": ["wind", "rain"]},
]

# Some activities are not just "needs daylight", they are built around a
# moment. A sunset cruise that leaves after the sun is down is not a sunset
# cruise however much of its window overlaps. Anchored activities require the
# moment itself to fall inside the departure.
ACTIVITY_ANCHORS = {
    "sunset_cruise": "sunset",
}

# CORRECTED 21 Aug 2026, on the operator's instruction.
#
# The question this app was built to answer is whether the boat should go out
# and whether the trip gets rained on. Cloud thickness and moon brightness
# decide neither. They describe how pretty the evening is, and an evening ride
# on a calm dry river is a good ride whatever the moon is doing.
#
# So these rules now produce NOTES ONLY. Nothing below can move a rating. The
# rating comes from rain, wind, thunderstorm and visibility, the same four
# things that rate every other departure.
RATING_INPUTS = ("rain", "wind", "thunderstorm", "visibility")

# The 19:00 departure now sells as one trip. These three no longer stand on
# their own: the sunset cruise cannot be served (the 17:00 boat is back before
# the sun is down), stargazing has no slot (dark starts after the last return),
# and the firefly run absorbed both. Existing bookings still carry the old
# names, so they are aliased rather than deleted.
ACTIVITY_ALIASES = {
    "firefly": "sunset_firefly",
    "sunset_cruise": "sunset_firefly",
    "stargazing": "sunset_firefly",
}
SUPERSEDED_ACTIVITIES = set(ACTIVITY_ALIASES)


def resolve_activity(activity_id: str) -> str:
    """Old booking labels map onto what the boat actually runs today."""
    return ACTIVITY_ALIASES.get(activity_id, activity_id)
NOTE_ONLY_INPUTS = ("cloud", "moon")

# Activity-specific rules. Note-producing, not rating-producing.
ACTIVITY_RULES = {
    # A clear sky gives a plain sunset. Broken cloud gives the good one.
    # Overcast gives nothing. So this one peaks in the middle.
    "sunset_cruise": {"cloud_good_band_pct": (20, 70), "cloud_poor_above_pct": 85},
    # Fireflies read best on a dark night.
    "firefly": {"moon_marginal_above_pct": 65, "gust_poor_kmh": 25, "rain_poor_mm_per_hour": 0.5},
    # Cloud is dominant for stargazing; moonlight is second.
    "stargazing": {"cloud_good_max_pct": 30, "cloud_marginal_max_pct": 60,
                   "moon_good_max_pct": 40, "moon_marginal_max_pct": 70},
}

# ---------------------------------------------------------------------------
# The combined 19:00 run: sunset, then fireflies.
#
# Decided 21 Aug 2026. Sunset falls around 19:26 all week, so the 17:00
# departure is back at the jetty before the sun is down and cannot show it.
# The 19:00 boat is the only one that can, and it was already the firefly run.
# Rather than compete for the same hull, they are one trip.
#
# The two halves want different things, so they are scored separately and the
# worse one sets the rating. That matters commercially: a washed-out sunset
# with a good firefly half is still a sellable evening, just under a different
# name, and the app should say so instead of colouring the whole run red.
#
# Phase windows are worked out from sunset on the day, not from the clock, so
# they follow the sun through the year.
# ---------------------------------------------------------------------------

COMBINED_TRIPS = {
    "sunset_firefly": {
        "name": "Evening Firefly Run",
        # DECIDED 21 Aug 2026 by the operator. The fireflies are the product and
        # set the rating. The sunset is a bonus: it can add a note, and it can
        # never pull the evening down. Over 181 evenings the firefly half held
        # up on 93 percent of nights and the sunset half on 32, so rating the
        # run on the worse half would have cancelled two nights in three for a
        # thing that was never promised.
        "primary_phase": "firefly",
        "bonus_phase": "sunset",
        "slot": "1900",
        "phases": [
            {
                "id": "sunset",
                "label": "Sunset half",
                # From leaving the jetty until the colour has gone.
                "from": "departure_start", "to_sunset_offset": +20,
                "exposure": "open",          # looking west over the estuary
                "thresholds": {
                    # Cloud is the one that peaks in the middle. A clear sky
                    # gives a plain sunset, broken cloud gives the good one,
                    # overcast gives nothing.
                    "cloud_good_band_pct": (20, 70),
                    "cloud_muted_above_pct": 70,
                    "cloud_poor_above_pct": 85,
                    # People are on an open deck looking west. Any rain spoils
                    # it; this is a lower bar than a daytime cruise.
                    "rain_marginal_mm_per_hour": 0.1,
                    "rain_poor_mm_per_hour": 0.5,
                    # Lower than the daytime open-water limit, because this is
                    # a sit-and-look trip, not a get-somewhere trip.
                    "gust_marginal_kmh": 22,
                    "gust_poor_kmh": 32,
                    # Haze swallows the sun before cloud does.
                    "visibility_marginal_km": 8,
                    "visibility_poor_km": 5,
                },
            },
            {
                "id": "firefly",
                "label": "Firefly half",
                # Allow the transit into the channels after the colour goes.
                "from_sunset_offset": +34, "to": "departure_end",
                "exposure": "sheltered",     # mangrove channels
                "thresholds": {
                    "rain_marginal_mm_per_hour": 0.2,
                    # DECIDED: 0.5 mm/h is where it stops being worth it under the canopy.
                    "rain_poor_mm_per_hour": 0.5,
                    # Fireflies shelter in wind and the boat drifts.
                    "gust_marginal_kmh": 18,
                    "gust_poor_kmh": 25,
                    # Moonlight competes with the display. This does not stop
                    # the trip, it sets what to promise at booking.
                    "moon_good_max_pct": 40,
                    "moon_marginal_max_pct": 75,
                    "moon_poor_above_pct": None,   # kept at None on purpose: the moon never stops a run
                },
            },
        ],
        # Minutes of firefly time below which the run is not worth selling as one.
        "min_firefly_minutes": 40,
    },
}

# ---------------------------------------------------------------------------
# Sheltered stops. Local knowledge. The model cannot infer any of this.
# ---------------------------------------------------------------------------
# TODO(operator): correct the minutes and the "cover" column. These are guesses.

SHELTER_STOPS = [
    {"id": "jetty",           "name": "Kuala Sepetang jetty",  "minutes_from_jetty": 0,
     "cover": "full",    "can_do": ["wait it out", "refreshments"]},
    {"id": "charcoal",        "name": "Charcoal factory",      "minutes_from_jetty": 10,
     "cover": "full",    "can_do": ["factory walk-through", "talk"]},
    {"id": "village",         "name": "Fishing village",       "minutes_from_jetty": 15,
     "cover": "partial", "can_do": ["village walk", "shelter under the walkways"]},
    {"id": "fish_farm",       "name": "Floating fish farm",    "minutes_from_jetty": 25,
     "cover": "full",    "can_do": ["feeding", "talk", "wait it out"]},
    {"id": "kuala_sangga",    "name": "Kuala Sangga",          "minutes_from_jetty": 45,
     "cover": "partial", "can_do": ["village visit", "food stop"]},
]

# What to do, by where the rain sits in the trip. Options come from the list
# above; the matching is the tool's job.
CONTINGENCY = {
    "dry":          "Run as planned.",
    "clears":       "Hold at the jetty 20 to 30 minutes, then run the full trip.",
    "arrives":      "Shorten the outbound leg or turn at the near point. Rain lands on the "
                    "return, when the boat is furthest from cover.",
    "intermittent": "Route via stops with cover and keep the open stretches short.",
    "throughout":   "Offer the alternative slot rather than running it wet end to end.",
}

# ---------------------------------------------------------------------------
# Forecast confidence by lead time.
#
# These bands are an ESTIMATE until Stage B measures them from the archive.
# `measured` flips to True once results/skill-by-lead.json exists.
# ---------------------------------------------------------------------------

# MEASURED 21 Aug 2026 by eval_stage_b.py: 93 dates, 558 departures, against
# Open-Meteo previous model runs at this exact location.
#
# The headline finding, and the reason `shape_shown` exists:
#
#   wet-or-dry    skill over baseline  0.41 (1d)  0.26 (3d)  0.21 (5d)  0.04 (7d)
#   rain shape    skill over baseline  0.04 (1d) -0.06 (3d) -0.08 (5d) -0.14 (7d)
#
# Whether a departure gets rain at all is genuinely forecastable out to about
# five days. WHERE in the two hours the rain sits is not: beyond tomorrow the
# forecast is worse than always guessing the commonest shape. So the rain strip
# is shown for today and tomorrow only, and further out the app reports wet or
# dry and says nothing about timing it cannot back up.

CONFIDENCE_TIERS = [
    {"max_lead_days": 1,  "tier": "firm",
     "usable": "whether a departure gets rain, called right 71% of the time, "
               "and where in the two hours it falls",
     "booking": "commit to specific slots",
     "shape_shown": True,  "measured_skill_wetdry": 0.41, "measured_skill_shape": 0.04},

    {"max_lead_days": 3,  "tier": "indicative",
     "usable": "whether a departure gets rain, called right 64% of the time. "
               "Timing inside the window is not reliable this far out",
     "booking": "take the booking, flag the slot provisional",
     "shape_shown": False, "measured_skill_wetdry": 0.26, "measured_skill_shape": -0.06},

    {"max_lead_days": 5,  "tier": "provisional",
     "usable": "whether the day is wet, called right 61% of the time, nothing finer",
     "booking": "take it with a reschedule clause, do not quote a slot",
     "shape_shown": False, "measured_skill_wetdry": 0.21, "measured_skill_shape": -0.08},

    {"max_lead_days": 16, "tier": "pattern",
     "usable": "no better than the seasonal average at this range",
     "booking": "climatology, not forecast",
     "shape_shown": False, "measured_skill_wetdry": 0.04, "measured_skill_shape": -0.14},
]

CONFIDENCE_MEASURED = True    # eval_stage_b.py, 21 Aug 2026, 558 departures
MEASUREMENT_SOURCE = "results/stage-b-horizon.json"

# ---------------------------------------------------------------------------
# Positioning. This string travels back with every tool result so the caveat
# reaches the reader instead of living only in the system prompt.
# ---------------------------------------------------------------------------

DISCLAIMER = (
    "Decision support for tour scheduling. Conditions are reported against the "
    "operator's own thresholds. This is not a statement that a departure is safe. "
    "The operator on the water owns the go or no-go call. Tide is not included."
)

RATINGS = ("good", "marginal", "poor")
SHAPES = ("dry", "clears", "arrives", "intermittent", "throughout")
