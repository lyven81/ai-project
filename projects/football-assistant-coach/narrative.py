"""
Generate fresh coaching narratives (highlight + concern) for all 22 players
in a single Claude call, based on their scores and profiles.
Much faster than 88 individual evaluation calls.
"""
import os
import json
import anthropic
from config import MODEL

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    timeout=30.0,
)


def generate_narratives(results: dict, players: list) -> dict:
    """
    Send all 22 players with their week scores to Claude in one call.
    Returns {player_id: {"highlight": str, "concern": str}}.
    Falls back to the existing notes in results if the call fails.
    """
    # Build a compact player summary list for the prompt
    player_lookup = {p["id"]: p for p in players}
    summaries = []
    for pid, data in results.items():
        player = player_lookup.get(pid, {})
        best_session  = max(data["sessions"], key=lambda s: data["sessions"][s]["total_score"])
        worst_session = min(data["sessions"], key=lambda s: data["sessions"][s]["total_score"])
        summaries.append({
            "id":           pid,
            "name":         data["name"],
            "position":     data["position"],
            "age":          data.get("age", ""),
            "strength":     player.get("strength", ""),
            "weakness":     player.get("weakness", ""),
            "form_score":   data["form_score"],
            "best_session": best_session,
            "best_score":   data["sessions"][best_session]["total_score"],
            "worst_session": worst_session,
            "worst_score":  data["sessions"][worst_session]["total_score"],
        })

    prompt = f"""You are a professional football head coach writing weekly training notes for your squad.

Below are 22 players with their training scores for this week.
For EACH player write:
- "highlight": one sentence (max 15 words) on what they did well, referencing their position or strength
- "concern": one sentence (max 15 words) on what they need to improve, or "No concerns this week." if form_score >= 70

Rules:
- Use plain, direct coaching language — no jargon
- Vary the language — do not repeat the same phrases across players
- Reflect the player's position, strength, weakness, and best/worst session
- Players with form_score below 50 should have a more serious concern

Players:
{json.dumps(summaries, indent=2)}

Respond ONLY with a valid JSON array in exactly this format:
[
  {{"id": <player_id>, "highlight": "<sentence>", "concern": "<sentence>"}},
  ...
]
Include all 22 players. No extra text outside the JSON array.
"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)
        return {int(item["id"]): {"highlight": item["highlight"], "concern": item["concern"]}
                for item in parsed}

    except Exception:
        # Fall back to whatever notes are already in results
        return {pid: {"highlight": data["highlight"], "concern": data["concern"]}
                for pid, data in results.items()}


def apply_narratives(results: dict, narratives: dict) -> dict:
    """Merge fresh narratives into a results dict (non-destructive copy)."""
    updated = {}
    for pid, data in results.items():
        updated[pid] = dict(data)
        if pid in narratives:
            updated[pid]["highlight"] = narratives[pid]["highlight"]
            updated[pid]["concern"]   = narratives[pid]["concern"]
            # Also update the Friday session notes so coach notes expanders are fresh
            if "Friday" in updated[pid]["sessions"]:
                updated[pid]["sessions"]["Friday"]["highlight"] = narratives[pid]["highlight"]
                updated[pid]["sessions"]["Friday"]["concern"]   = narratives[pid]["concern"]
    return updated
