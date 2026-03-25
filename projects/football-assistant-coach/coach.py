import os
import json
import random
import anthropic
from config import MODEL, MAX_INDIVIDUAL, MAX_CHEMISTRY, MAX_UNIVERSAL, SESSION_FOCUS

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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


def evaluate_player(player: dict, session: str, session_desc: str) -> dict:
    """Call Claude to evaluate a single player in one training session. Returns scores + narrative."""
    focus = SESSION_FOCUS[session]
    system_prompt = POSITION_PERSONAS[player["position"]]
    user_prompt = _build_prompt(player, session, session_desc, focus)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        result = json.loads(raw)

        # Clamp values to valid range
        result["individual_score"] = max(0, min(MAX_INDIVIDUAL, int(result["individual_score"])))
        result["chemistry_score"]  = max(0, min(MAX_CHEMISTRY,  int(result["chemistry_score"])))
        result["universal_score"]  = max(0, min(MAX_UNIVERSAL,  int(result["universal_score"])))
        result["total_score"] = (
            result["individual_score"] + result["chemistry_score"] + result["universal_score"]
        )
        return result

    except Exception as e:
        # Fallback: generate a plausible score from base_form with noise
        base = player.get("base_form", 65)
        noise = random.randint(-8, 8)
        base_clamped = max(20, min(95, base + noise))
        ind  = int(base_clamped * (MAX_INDIVIDUAL / 100))
        chem = int(base_clamped * (MAX_CHEMISTRY / 100))
        uni  = int(base_clamped * (MAX_UNIVERSAL / 100))
        return {
            "individual_score": ind,
            "chemistry_score": chem,
            "universal_score": uni,
            "total_score": ind + chem + uni,
            "highlight": "Consistent performance in training.",
            "concern": f"(Evaluation fallback: {str(e)[:60]})",
        }
