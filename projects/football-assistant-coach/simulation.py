from concurrent.futures import ThreadPoolExecutor, as_completed
from config import SESSION_WEIGHTS, SESSION_DESCRIPTIONS, FORM_THIS_WEEK, FORM_LAST_WEEK, THRESHOLD_UNUSED
from coach import evaluate_player

SESSIONS_ORDER = ["Monday", "Wednesday", "Thursday", "Friday"]
MAX_WORKERS = 5   # conservative concurrency — avoids 429 rate limit errors


def run_week(players: list, last_week_scores: dict = None, progress_callback=None) -> dict:
    """
    Run one full training week (4 sessions × 22 players = 88 calls) in parallel.
    Uses a thread pool so all calls fire concurrently instead of sequentially.
    """
    # Build the full task list: one entry per (player, session)
    tasks = [
        (player, session, SESSION_DESCRIPTIONS[session])
        for player in players
        for session in SESSIONS_ORDER
    ]

    # Collect raw results keyed by (player_id, session)
    raw: dict = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_map = {
            pool.submit(evaluate_player, player, session, desc): (player, session)
            for player, session, desc in tasks
        }
        for future in as_completed(future_map):
            player, session = future_map[future]
            try:
                result = future.result()
            except Exception as e:
                # evaluate_player already has a fallback, but guard here too
                result = {
                    "individual_score": 0, "chemistry_score": 0, "universal_score": 0,
                    "total_score": 0,
                    "highlight": "Evaluation unavailable.",
                    "concern": f"API error: {str(e)[:60]}",
                }
            raw[(player["id"], session)] = result
            if progress_callback:
                progress_callback(player["name"], session, result["total_score"])

    # Aggregate per player
    results = {}
    for player in players:
        pid = player["id"]
        session_results = {s: raw[(pid, s)] for s in SESSIONS_ORDER}

        weekly_score = sum(
            session_results[s]["total_score"] * SESSION_WEIGHTS[s]
            for s in SESSIONS_ORDER
        )

        if last_week_scores and pid in last_week_scores:
            form_score = (weekly_score * FORM_THIS_WEEK) + (last_week_scores[pid] * FORM_LAST_WEEK)
        else:
            form_score = weekly_score

        highlights = [session_results[s]["highlight"] for s in SESSIONS_ORDER]
        concerns   = [session_results[s]["concern"] for s in SESSIONS_ORDER
                      if session_results[s]["concern"] != "No concerns today"]

        results[pid] = {
            "name": player["name"],
            "position": player["position"],
            "age": player["age"],
            "sessions": session_results,
            "weekly_score": round(weekly_score, 1),
            "form_score": round(form_score, 1),
            "highlight": highlights[-1],
            "concern": concerns[0] if concerns else "No concerns this week",
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
