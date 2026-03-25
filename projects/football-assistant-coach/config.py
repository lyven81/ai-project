MODEL = "claude-haiku-4-5-20251001"

# Scoring maximums
MAX_INDIVIDUAL = 35
MAX_CHEMISTRY = 50
MAX_UNIVERSAL = 15
MAX_TOTAL = 100

# Session weights (must sum to 1.0)
SESSION_WEIGHTS = {
    "Monday":    0.15,
    "Wednesday": 0.25,
    "Thursday":  0.25,
    "Friday":    0.35,
}

# Session focus: weights for (individual, chemistry, universal) scoring
SESSION_FOCUS = {
    "Monday":    {"individual": 0.30, "chemistry": 0.10, "universal": 0.60},
    "Wednesday": {"individual": 0.70, "chemistry": 0.10, "universal": 0.20},
    "Thursday":  {"individual": 0.10, "chemistry": 0.70, "universal": 0.20},
    "Friday":    {"individual": 0.333, "chemistry": 0.333, "universal": 0.334},
}

SESSION_DESCRIPTIONS = {
    "Monday":    "Fitness & Conditioning",
    "Wednesday": "Position-Specific Drill",
    "Thursday":  "Tactical Shape & Pressing",
    "Friday":    "Full Team Scrimmage",
}

# Form weighting
FORM_THIS_WEEK = 0.60
FORM_LAST_WEEK = 0.40

# Selection thresholds
THRESHOLD_LINEUP  = 65
THRESHOLD_BENCH   = 50
THRESHOLD_UNUSED  = 40
# Below THRESHOLD_UNUSED for 2 consecutive weeks → transfer shortlist

# Formation options and positional quotas
FORMATIONS = {
    "4-3-3": {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3},
    "4-4-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "3-5-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
}

DEFAULT_FORMATION = "4-3-3"
