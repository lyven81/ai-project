from config import SESSION_WEIGHTS, SESSION_DESCRIPTIONS, FORM_THIS_WEEK, FORM_LAST_WEEK, THRESHOLD_UNUSED
from coach import evaluate_player


SESSIONS_ORDER = ["Monday", "Wednesday", "Thursday", "Friday"]


def run_week(players: list, last_week_scores: dict = None, progress_callback=None) -> dict:
    """
    Run one full training week (4 sessions) for all 22 players.
    Returns:
        {
          player_id: {
            "name": ..., "position": ...,
            "sessions": { "Monday": result_dict, ... },
            "weekly_score": float,
            "form_score": float,   # weighted with last week
            "highlight": str,      # best highlight from the week
            "concern": str,        # worst concern from the week
          }
        }
    """
    results = {}

    for player in players:
        pid = player["id"]
        session_results = {}

        for session in SESSIONS_ORDER:
            desc = SESSION_DESCRIPTIONS[session]
            eval_result = evaluate_player(player, session, desc)
            session_results[session] = eval_result
            if progress_callback:
                progress_callback(player["name"], session, eval_result["total_score"])

        # Compute weighted weekly score
        weekly_score = sum(
            session_results[s]["total_score"] * SESSION_WEIGHTS[s]
            for s in SESSIONS_ORDER
        )

        # Apply form rolling average with last week
        if last_week_scores and pid in last_week_scores:
            form_score = (weekly_score * FORM_THIS_WEEK) + (last_week_scores[pid] * FORM_LAST_WEEK)
        else:
            form_score = weekly_score

        # Pick best highlight and worst concern from the week
        highlights = [session_results[s]["highlight"] for s in SESSIONS_ORDER]
        concerns   = [session_results[s]["concern"] for s in SESSIONS_ORDER if session_results[s]["concern"] != "No concerns today"]
        best_highlight = highlights[-1]  # Friday scrimmage is highest-weighted
        worst_concern  = concerns[0] if concerns else "No concerns this week"

        results[pid] = {
            "name": player["name"],
            "position": player["position"],
            "age": player["age"],
            "sessions": session_results,
            "weekly_score": round(weekly_score, 1),
            "form_score": round(form_score, 1),
            "highlight": best_highlight,
            "concern": worst_concern,
        }

    return results


def check_transfer_risk(this_week: dict, last_week: dict) -> list:
    """
    Return list of player ids who scored below THRESHOLD_UNUSED in both this week and last week.
    """
    if not last_week:
        return []
    at_risk = []
    for pid, data in this_week.items():
        if pid in last_week:
            if data["form_score"] < THRESHOLD_UNUSED and last_week[pid] < THRESHOLD_UNUSED:
                at_risk.append(pid)
    return at_risk
