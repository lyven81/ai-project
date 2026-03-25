from datetime import datetime
from config import ROUNDS, STARTING_BUDGET, ROI_BENCHMARK


def build_report(agents):
    ranked = sorted(agents, key=lambda a: a.budget, reverse=True)

    scale = [a.channel for a in ranked if a.total_roi > 10 and not a.flagged]
    cut = [a.channel for a in ranked if a.flagged or a.total_roi < -10]
    hold = [a.channel for a in ranked if a.channel not in scale and a.channel not in cut]

    return {
        "ranked": ranked,
        "scale": scale,
        "cut": cut,
        "hold": hold,
    }


def save_markdown(agents, report, filepath="simulation_report.md"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Social Media Marketer — Simulation Report",
        f"\nGenerated: {now}  ",
        f"Rounds: {ROUNDS} | Starting budget per agent: ${STARTING_BUDGET:.0f} | Benchmark: {ROI_BENCHMARK * 100:.0f}% uplift",
        "\n---\n",
        "## Final Leaderboard\n",
        "| Rank | Agent | Channel | Final Budget | Total ROI | Avg Uplift | Rounds Hit Benchmark | Status |",
        "|------|-------|---------|-------------|-----------|-----------|---------------------|--------|",
    ]

    for i, agent in enumerate(report["ranked"], 1):
        status = "FLAGGED — REVIEW" if agent.flagged else "OK"
        lines.append(
            f"| {i} | {agent.persona['name']} | {agent.channel} "
            f"| ${agent.budget:.0f} | {agent.total_roi:+.1f}% "
            f"| {agent.avg_uplift * 100:.1f}% "
            f"| {agent.rounds_above_benchmark}/{ROUNDS} | {status} |"
        )

    lines += [
        "\n---\n",
        "## CMO Recommendations\n",
    ]
    if report["scale"]:
        lines.append(f"**Scale up:** {', '.join(report['scale'])}  ")
        lines.append("These channels beat the benchmark consistently. Increase budget allocation.\n")
    if report["hold"]:
        lines.append(f"**Hold:** {', '.join(report['hold'])}  ")
        lines.append("Performance is acceptable. Monitor for one more cycle before deciding.\n")
    if report["cut"]:
        lines.append(f"**Cut / Review:** {', '.join(report['cut'])}  ")
        lines.append("These channels missed the benchmark repeatedly. Pause spend and investigate.\n")

    lines += ["\n---\n", "## Round-by-Round Detail\n"]

    for agent in agents:
        lines.append(f"### {agent.name}\n")
        for h in agent.history:
            c = h["campaign"]
            lines.append(
                f"- **Round {h['round']}** — {c['objective']} → {c['segment']} "
                f"| Uplift: {h['uplift'] * 100:.1f}% "
                f"| Allocated: ${h['allocated']:.0f} "
                f"| Net: ${h['net']:+.0f} "
                f"| **{h['outcome']}**"
            )
            lines.append(f"  - *{h['reasoning']}*")
        lines.append(f"\nFinal budget: **${agent.budget:.0f}** | ROI: **{agent.total_roi:+.1f}%**\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
