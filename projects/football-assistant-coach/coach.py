import os
import json
import time
import random
import anthropic
from config import MODEL, MAX_INDIVIDUAL, MAX_CHEMISTRY, MAX_UNIVERSAL, SESSION_FOCUS

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    timeout=30.0,
)

POSITION_PERSONAS = {
    "GK": (
        "You are a goalkeeping coach. You evaluate goalkeeper performance in training with deep focus on "
        "shot-stopping, command of area, distribution, communication, and organising the defensive line."
    ),
    "DEF": (
        "You are a defensive coach. You evaluate defenders on positioning, tackling, aerial duels, "
        "pressing discipline, and how well they hold their shape in training drills."
    ),
    "MID": (
        "You are a midfield coach. You evaluate midfielders on passing range, pressing intensity, "
        "defensive cover, attacking transitions, and combination play with teammates."
    ),
    "FWD": (
        "You are a forward/attacking coach. You evaluate forwards on finishing, movement off the ball, "
        "pressing triggers, hold-up play, and runs in behind the defensive line."
    ),
}

# Coaching notes used when a session falls back to baseline scores
_HIGHLIGHT_POOL = [
    "Showed good attitude and effort throughout the session.",
    "Worked hard and maintained focus for the full session.",
    "Contributed positively to the group drills.",
    "Demonstrated solid fundamentals in positional work.",
    "Good communication and awareness shown during the session.",
]
_CONCERN_POOL = [
    "Continue working on consistency in high-pressure moments.",
    "Focus on sharpening decision-making under fatigue.",
    "More intensity needed in pressing sequences.",
    "Work on first touch and composure in tight spaces.",
    "Tracking runs and defensive transitions need attention.",
]


def _build_prompt(player: dict, session: str, session_desc: str, focus: dict) -> str:
    return f"""
You are evaluating {player['name']}, a {player['position']} (age {player['age']}).
Style: {player['style']}
Strength: {player['strength']}
Weakness: {player['weakness']}

Today's training session: {session} — {session_desc}
Session focus weights: Individual {int(focus['individual']*100)}%, Team Chemistry {int(focus['chemistry']*100)}%, Universal {int(focus['universal']*100)}%

Evaluate this player's performance in today's session.

Scoring rules:
- individual_score: 0 to {MAX_INDIVIDUAL}. Measures position-specific technical performance.
- chemistry_score: 0 to {MAX_CHEMISTRY}. Measures selflessness, support runs, tracking back, pressing coordination, communication. THIS is the most important score — reward team play highly.
- universal_score: 0 to {MAX_UNIVERSAL}. Measures fitness, attitude, discipline, focus.

Apply today's focus weights when deciding how demanding to be in each area.
A player strong in {player['strength']} should score well in relevant areas.
A player weak in {player['weakness']} should show lower scores where that weakness is tested.

Use some realistic variation — not every session is perfect.

Respond ONLY with valid JSON in exactly this format:
{{
  "individual_score": <integer 0-{MAX_INDIVIDUAL}>,
  "chemistry_score": <integer 0-{MAX_CHEMISTRY}>,
  "universal_score": <integer 0-{MAX_UNIVERSAL}>,
  "highlight": "<one sentence: what the player did well today>",
  "concern": "<one sentence: what the player needs to improve, or 'No concerns today' if strong session>"
}}
"""


def _baseline_result(player: dict) -> dict:
    """Generate a realistic score from base_form when the API is unavailable."""
    base = player.get("base_form", 65)
    noise = random.randint(-6, 6)
    score = max(20, min(95, base + noise))
    ind  = int(score * (MAX_INDIVIDUAL / 100))
    chem = int(score * (MAX_CHEMISTRY  / 100))
    uni  = int(score * (MAX_UNIVERSAL  / 100))
    return {
        "individual_score": ind,
        "chemistry_score":  chem,
        "universal_score":  uni,
        "total_score":      ind + chem + uni,
        "highlight":        random.choice(_HIGHLIGHT_POOL),
        "concern":          random.choice(_CONCERN_POOL),
    }


def evaluate_player(player: dict, session: str, session_desc: str) -> dict:
    """
    Call Claude to evaluate a single player in one training session.
    Retries up to 3 times on rate-limit errors with exponential backoff.
    Falls back to baseline scores if all retries are exhausted.
    """
    focus         = SESSION_FOCUS[session]
    system_prompt = POSITION_PERSONAS[player["position"]]
    user_prompt   = _build_prompt(player, session, session_desc, focus)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw    = response.content[0].text.strip()
            result = json.loads(raw)

            result["individual_score"] = max(0, min(MAX_INDIVIDUAL, int(result["individual_score"])))
            result["chemistry_score"]  = max(0, min(MAX_CHEMISTRY,  int(result["chemistry_score"])))
            result["universal_score"]  = max(0, min(MAX_UNIVERSAL,  int(result["universal_score"])))
            result["total_score"] = (
                result["individual_score"] + result["chemistry_score"] + result["universal_score"]
            )
            return result

        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)   # 1s → 2s → 4s
                continue
            return _baseline_result(player)

        except (json.JSONDecodeError, KeyError, ValueError):
            # Malformed response — retry once, then fall back
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return _baseline_result(player)

        except Exception:
            return _baseline_result(player)
