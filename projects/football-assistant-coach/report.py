from config import (
    FORMATIONS, THRESHOLD_LINEUP, THRESHOLD_BENCH, THRESHOLD_UNUSED
)


def score_formation_fit(week_results: dict, formation: str) -> float:
    """
    Score how well the current top-form players fit a given formation.
    For each position slot required, take the top N players by form score.
    Returns the sum of those form scores — higher = better natural fit.
    """
    quotas = FORMATIONS[formation]
    by_position = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for pid, data in week_results.items():
        by_position[data["position"]].append(data["form_score"])

    for pos in by_position:
        by_position[pos].sort(reverse=True)

    total = 0.0
    for pos, count in quotas.items():
        total += sum(by_position[pos][:count])
    return round(total, 1)


def recommend_formation(week_results: dict) -> tuple:
    """
    Return (best_formation: str, fit_scores: dict).
    fit_scores maps each formation to its fit score.
    """
    fit_scores = {f: score_formation_fit(week_results, f) for f in FORMATIONS}
    best = max(fit_scores, key=fit_scores.get)
    return best, fit_scores


def select_squad(week_results: dict, formation: str, transfer_risk_ids: list) -> dict:
    """
    Given week_results dict and a formation, return:
    {
      "lineup": [player_dicts...],        # exactly 11
      "bench": [player_dicts...],         # exactly 5 (1 GK + coverage)
      "unused": [player_dicts...],        # remaining
      "transfer_shortlist": [player_dicts...],
      "formation": str,
      "quotas": {GK: n, DEF: n, MID: n, FWD: n}
    }
    """
    quotas = FORMATIONS[formation]
    by_position = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for pid, data in week_results.items():
        pos = data["position"]
        by_position[pos].append({**data, "id": pid})

    # Sort each position group by form_score descending
    for pos in by_position:
        by_position[pos].sort(key=lambda x: x["form_score"], reverse=True)

    lineup = []
    remaining = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for pos, count in quotas.items():
        eligible = [p for p in by_position[pos] if p["form_score"] >= THRESHOLD_LINEUP]
        # Fill quota from eligible; fall back to best available if not enough eligible
        selected = eligible[:count]
        if len(selected) < count:
            fallback = [p for p in by_position[pos] if p not in selected]
            selected += fallback[: count - len(selected)]
        lineup.extend(selected)
        remaining[pos] = [p for p in by_position[pos] if p not in selected]

    # --- Bench selection: 1 GK + fill remaining 4 spots with best available ---
    bench = []

    # Always pick best remaining GK for bench
    if remaining["GK"]:
        bench.append(remaining["GK"][0])
        remaining["GK"] = remaining["GK"][1:]

    # Pool all remaining outfield players sorted by form_score
    outfield_pool = (
        remaining["DEF"] + remaining["MID"] + remaining["FWD"]
    )
    outfield_pool.sort(key=lambda x: x["form_score"], reverse=True)

    bench_spots_left = 5 - len(bench)
    bench.extend(outfield_pool[:bench_spots_left])
    benched_ids = {p["id"] for p in bench}

    # --- Unused: everyone not in lineup or bench ---
    lineup_ids = {p["id"] for p in lineup}
    unused = [
        p for pos_list in remaining.values()
        for p in pos_list
        if p["id"] not in lineup_ids and p["id"] not in benched_ids
    ]
    # Also add any GK not benched
    unused.sort(key=lambda x: x["form_score"], reverse=True)

    # --- Transfer shortlist ---
    transfer_shortlist = [
        p for p in unused + bench
        if p["id"] in transfer_risk_ids
    ]

    return {
        "formation": formation,
        "quotas": quotas,
        "lineup": lineup,
        "bench": bench,
        "unused": unused,
        "transfer_shortlist": transfer_shortlist,
    }


def build_summary(selection: dict, week_results: dict) -> str:
    """Plain text summary for CLI output or export."""
    lines = []
    lines.append(f"=== MATCH-DAY SELECTION ({selection['formation']}) ===\n")

    lines.append("STARTING XI:")
    for p in selection["lineup"]:
        lines.append(f"  [{p['position']}] {p['name']:20s}  Form: {p['form_score']}")

    lines.append("\nBENCH (5):")
    for p in selection["bench"]:
        lines.append(f"  [{p['position']}] {p['name']:20s}  Form: {p['form_score']}")

    lines.append("\nUNUSED:")
    for p in selection["unused"]:
        flag = " *** TRANSFER RISK ***" if p["id"] in {t["id"] for t in selection["transfer_shortlist"]} else ""
        lines.append(f"  [{p['position']}] {p['name']:20s}  Form: {p['form_score']}{flag}")

    if selection["transfer_shortlist"]:
        lines.append("\n--- TRANSFER SHORTLIST ---")
        for p in selection["transfer_shortlist"]:
            lines.append(f"  {p['name']} ({p['position']})  Form: {p['form_score']:.1f}")

    return "\n".join(lines)
