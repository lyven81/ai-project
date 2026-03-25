import os
import sys

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import ROUNDS, STARTING_BUDGET, ROI_BENCHMARK
from data import load_campaigns, channel_stats
from agents import MarketingAgent, PERSONAS
from simulation import run_round
from report import build_report, save_markdown

console = Console()


# ── Display helpers ──────────────────────────────────────────────────────────

def print_header():
    console.print(
        Panel.fit(
            "[bold cyan]SOCIAL MEDIA MARKETER[/bold cyan]\n"
            "[dim]Multi-Agent Marketing Channel Simulation[/dim]\n"
            "[dim]Powered by Claude AI[/dim]",
            border_style="cyan",
        )
    )


def print_channel_stats(campaigns):
    stats = channel_stats(campaigns)
    table = Table(title="Channel Baseline (from dataset)", show_header=True, header_style="bold")
    table.add_column("Channel", width=14)
    table.add_column("Campaigns", width=10, justify="right")
    table.add_column("Avg Uplift", width=11, justify="right")
    table.add_column("Best", width=8, justify="right")
    table.add_column("Worst", width=8, justify="right")

    benchmark_color = lambda v: "green" if v >= ROI_BENCHMARK else "red"
    for ch, s in sorted(stats.items(), key=lambda x: x[1]["avg"], reverse=True):
        color = benchmark_color(s["avg"])
        table.add_row(
            ch,
            str(s["count"]),
            f"[{color}]{s['avg'] * 100:.1f}%[/{color}]",
            f"{s['best'] * 100:.1f}%",
            f"{s['worst'] * 100:.1f}%",
        )
    console.print(table)
    console.print(f"[dim]Benchmark: {ROI_BENCHMARK * 100:.0f}% uplift minimum[/dim]\n")


def print_round_result(agent, record):
    color = "green" if record["outcome"] == "PROFIT" else "red"
    console.print(f"  [bold]{agent.persona['name']}[/bold] [{agent.channel}]")
    c = record["campaign"]
    console.print(
        f"    Picked: {c['objective']} → {c['segment']} | "
        f"Uplift: {record['uplift'] * 100:.1f}% | "
        f"Allocated: ${record['allocated']:.0f} | "
        f"Net: [{color}]${record['net']:+.0f}[/{color}] [{color}]{record['outcome']}[/{color}]"
    )
    console.print(f"    [dim]{record['reasoning']}[/dim]")


def print_leaderboard(report):
    table = Table(title="Final Leaderboard", show_header=True, header_style="bold cyan")
    table.add_column("Rank", width=5)
    table.add_column("Agent", width=10)
    table.add_column("Channel", width=14)
    table.add_column("Final Budget", width=13, justify="right")
    table.add_column("Total ROI", width=10, justify="right")
    table.add_column("Avg Uplift", width=11, justify="right")
    table.add_column("Hit Benchmark", width=14, justify="center")
    table.add_column("Status", width=16)

    for i, agent in enumerate(report["ranked"], 1):
        roi_color = "green" if agent.total_roi >= 0 else "red"
        status_text = "[red]FLAGGED — REVIEW[/red]" if agent.flagged else "[green]OK[/green]"
        table.add_row(
            str(i),
            agent.persona["name"],
            agent.channel,
            f"${agent.budget:.0f}",
            f"[{roi_color}]{agent.total_roi:+.1f}%[/{roi_color}]",
            f"{agent.avg_uplift * 100:.1f}%",
            f"{agent.rounds_above_benchmark}/{ROUNDS}",
            status_text,
        )

    console.print(table)


def print_recommendations(report):
    console.print("\n[bold]── CMO RECOMMENDATIONS ──[/bold]\n")
    if report["scale"]:
        console.print(f"[bold green]SCALE UP:[/bold green]  {', '.join(report['scale'])}")
        console.print("[dim]  Consistent performance above benchmark. Increase budget.[/dim]")
    if report["hold"]:
        console.print(f"[bold yellow]HOLD:[/bold yellow]      {', '.join(report['hold'])}")
        console.print("[dim]  Acceptable. Monitor one more cycle before deciding.[/dim]")
    if report["cut"]:
        console.print(f"[bold red]CUT / REVIEW:[/bold red] {', '.join(report['cut'])}")
        console.print("[dim]  Missed benchmark repeatedly. Pause spend and investigate.[/dim]")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print_header()

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("\n[red]ANTHROPIC_API_KEY is not set.[/red]")
        console.print("Open [cyan].env[/cyan] in this folder, paste your key, then re-run the app.")
        console.print("See USER_GUIDE.md for instructions.\n")
        input("Press Enter to exit...")
        sys.exit(1)

    # Load data
    console.print("\n[dim]Loading campaign data...[/dim]")
    try:
        campaigns = load_campaigns()
    except FileNotFoundError:
        console.print("[red]campaigns.csv not found. Make sure it is in the same folder as main.py.[/red]")
        input("Press Enter to exit...")
        sys.exit(1)

    console.print(f"[dim]Loaded {len(campaigns)} campaigns[/dim]\n")
    print_channel_stats(campaigns)

    # Create agents — one per channel
    agents = [MarketingAgent(ch) for ch in PERSONAS]

    console.print(
        f"[bold]Starting simulation: {len(agents)} agents, "
        f"{ROUNDS} rounds, ${STARTING_BUDGET:.0f} budget each[/bold]\n"
    )

    # Simulation loop
    for round_num in range(1, ROUNDS + 1):
        console.print(f"[bold cyan]━━ Round {round_num} of {ROUNDS} ━━[/bold cyan]")
        for agent in agents:
            record = run_round(agent, campaigns, round_num)
            print_round_result(agent, record)
        console.print()

    # Results
    console.print("[bold cyan]━━ Final Results ━━[/bold cyan]\n")
    report = build_report(agents)
    print_leaderboard(report)
    print_recommendations(report)

    # Save report
    saved = save_markdown(agents, report)
    console.print(f"\n[dim]Full report saved → {saved}[/dim]\n")

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
