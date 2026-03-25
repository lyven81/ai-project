"""CLI entry point — run from terminal: python main.py"""
import os
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from players import PLAYERS
from simulation import run_week, check_transfer_risk
from report import select_squad, build_summary
from config import DEFAULT_FORMATION, FORMATIONS

console = Console()


def main():
    console.print(Panel.fit("[bold green]Football Assistant Coach[/bold green]\nAI-powered player selection system", border_style="green"))

    # Formation selection
    console.print("\nAvailable formations:")
    for i, f in enumerate(FORMATIONS.keys(), 1):
        console.print(f"  {i}. {f}")
    choice = console.input("\nPick formation (1/2/3) [default: 4-3-3]: ").strip()
    formation_map = {str(i): f for i, f in enumerate(FORMATIONS.keys(), 1)}
    formation = formation_map.get(choice, DEFAULT_FORMATION)

    console.print(f"\n[cyan]Formation selected:[/cyan] {formation}")

    simulate_two = console.input("Simulate two weeks for form rolling average? (y/n) [default: n]: ").strip().lower()

    last_week_scores = None
    if simulate_two == "y":
        console.print("\n[yellow]Running Week 1...[/yellow]")
        week1 = run_week(PLAYERS)
        last_week_scores = {pid: d["weekly_score"] for pid, d in week1.items()}
        console.print("[green]Week 1 done.[/green]")

    console.print("\n[yellow]Running training week (4 sessions × 22 players)...[/yellow]")
    results = run_week(PLAYERS, last_week_scores=last_week_scores)
    console.print("[green]Training complete.[/green]\n")

    transfer_risk = check_transfer_risk(
        results,
        {pid: s for pid, s in last_week_scores.items()} if last_week_scores else {}
    )
    selection = select_squad(results, formation, transfer_risk)

    # Print summary table
    table = Table(title=f"Squad Rankings — Form Score ({formation})")
    table.add_column("Player", style="white")
    table.add_column("Pos", style="cyan", justify="center")
    table.add_column("Form", style="bold", justify="right")
    table.add_column("Status", justify="center")

    all_players = sorted(results.values(), key=lambda x: x["form_score"], reverse=True)
    lineup_names = {p["name"] for p in selection["lineup"]}
    bench_names  = {p["name"] for p in selection["bench"]}
    risk_names   = {p["name"] for p in selection["transfer_shortlist"]}

    for d in all_players:
        if d["name"] in lineup_names:
            status = "[green]Starting XI[/green]"
        elif d["name"] in bench_names:
            status = "[yellow]Bench[/yellow]"
        elif d["name"] in risk_names:
            status = "[red]Transfer Risk[/red]"
        else:
            status = "[dim]Unused[/dim]"
        table.add_row(d["name"], d["position"], str(d["form_score"]), status)

    console.print(table)
    console.print()
    console.print(build_summary(selection, results))


if __name__ == "__main__":
    main()
