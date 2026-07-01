"""CLI for the fitness agents.

    polaris-fitness analyze activity.gpx --goal "run a sub-25 5K" --log
    polaris-fitness analyze activity.gpx --save report.md   # export full report
    polaris-fitness parse activity.gpx          # just show parsed metrics
    polaris-fitness log activity.gpx            # record a session for progress tracking
    polaris-fitness trend                        # fitness/fatigue/form over time
    polaris-fitness history                      # list logged sessions
    polaris-fitness schedule --goal "sub-25 5K" --export-ics plan.ics
    polaris-fitness agents                       # list markdown agents
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from polaris_core.console import console
from rich.markdown import Markdown
from rich.table import Table

from fitness_agents.agents import list_agents
from fitness_agents.graph import build_graph
from fitness_agents.history import clear_history, compute_trends, list_sessions, log_session
from fitness_agents.metrics import summarize
from fitness_agents.parsers import parse_file

app = typer.Typer(
    help="Fitness MD agents — analyze files, build a growth plan.",
    no_args_is_help=True,
)


def _log_files(files) -> int:
    """Parse + record each file as a session. Returns how many were logged."""
    logged = 0
    for f in files:
        records = parse_file(f)
        summary = summarize(records)
        dates = [r.timestamp for r in records if r.timestamp]
        log_session(summary, source=str(f), when=dates[0] if dates else None)
        logged += 1
    return logged


@app.command()
def agents() -> None:
    """List the available markdown-defined agents."""
    names = list_agents()
    console.print("Agents:" if names else "[yellow]No agent markdown files found.[/]")
    for n in names:
        console.print(f"  • {n}")


@app.command()
def parse(file: str) -> None:
    """Parse a fitness file and print its computed metrics."""
    records = parse_file(file)
    console.print(f"[green]Parsed {len(records)} records.[/]\n")
    console.print(summarize(records).to_prompt())


@app.command()
def analyze(
    files: list[str] = typer.Argument(..., help="One or more fitness files."),
    goal: str = typer.Option("", "--goal", "-g", help="Optional fitness goal."),
    save: Path | None = typer.Option(
        None, "--save", "-s", help="Write the full report (metrics + analysis + plan) to Markdown."
    ),
    log: bool = typer.Option(
        False, "--log", "-l", help="Also record these sessions in the progress history."
    ),
) -> None:
    """Run the full pipeline: parse → analyze → plan → review."""
    graph = build_graph()
    result = graph.invoke({"files": list(files), "goal": goal})
    analysis = result.get("analysis", "(none)")
    plan = result.get("review") or result.get("plan", "(none)")

    if result.get("trend_text"):
        console.rule("Progress")
        console.print(result["trend_text"])
    console.rule("Analysis")
    console.print(Markdown(analysis))
    console.rule("Growth Plan (reviewed)")
    console.print(Markdown(plan))

    if save is not None:
        report = _build_report(files, goal, result.get("metrics_text", ""), analysis, plan)
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(report, encoding="utf-8")
        console.print(f"\n[green]✓ Report saved →[/] {save}")

    if log:
        n = _log_files(files)
        console.print(f"[green]✓ Logged {n} session(s) to history.[/]")


@app.command()
def log(files: list[str] = typer.Argument(..., help="Fitness file(s) to record.")) -> None:
    """Record one or more sessions for progress tracking (no AI)."""
    n = _log_files(files)
    console.print(f"[green]✓ Logged {n} session(s).[/]")


@app.command()
def trend() -> None:
    """Show fitness (CTL), fatigue (ATL), and form (TSB) trends over time."""
    trends = compute_trends()
    if not trends:
        console.print("[yellow]No history yet.[/] Log with [bold]polaris-fitness log <file>[/].")
        return
    console.print(trends.to_prompt())


@app.command()
def history(limit: int = typer.Option(20, "--limit", "-n", help="How many to show.")) -> None:
    """List logged sessions."""
    rows = list_sessions(limit=limit)
    if not rows:
        console.print("[yellow]No sessions logged yet.[/]")
        return
    table = Table(title="Training history")
    table.add_column("Date")
    table.add_column("Source")
    table.add_column("km", justify="right")
    table.add_column("Load", justify="right")
    for r in rows:
        date = r["date"][:16].replace("T", " ")
        km = f"{r['distance_km']:.1f}" if r["distance_km"] else "-"
        load = f"{r['training_load']:.0f}" if r["training_load"] else "-"
        table.add_row(date, Path(r["source"]).name, km, load)
    console.print(table)


@app.command(name="clear-history")
def clear_history_cmd(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete all logged sessions."""
    if not yes and not typer.confirm("Delete all training history?"):
        console.print("Aborted.")
        return
    clear_history()
    console.print("[green]✓ History cleared.[/]")


@app.command()
def schedule(
    goal: str = typer.Option(..., "--goal", "-g", help="Training goal for the week."),
    files: list[str] = typer.Argument(None, help="Optional file(s) for context."),
    export_ics: Path | None = typer.Option(
        None, "--export-ics", help="Write the week to an importable .ics calendar."
    ),
) -> None:
    """Generate a structured one-week schedule (optionally export to calendar)."""
    from fitness_agents.schedule import export_ics as _export_ics
    from fitness_agents.schedule import generate_schedule

    context = ""
    if files:
        context = "\n\n".join(f"{f}\n{summarize(parse_file(f)).to_prompt()}" for f in files)
    week = generate_schedule(goal, context=context)

    table = Table(title=f"Weekly schedule — {week.goal}")
    table.add_column("Day", style="cyan")
    table.add_column("Session", style="bold")
    table.add_column("Details")
    table.add_column("min", justify="right")
    for w in week.workouts:
        table.add_row(w.day, w.title, w.description, str(w.duration_min))
    console.print(table)

    if export_ics is not None:
        path = _export_ics(week, export_ics)
        console.print(f"[green]✓ Calendar exported →[/] {path}")


def _build_report(files, goal: str, metrics: str, analysis: str, plan: str) -> str:
    """Assemble a shareable Markdown report."""
    return "\n".join(
        [
            "# Fitness Report",
            f"_Generated {datetime.now():%Y-%m-%d %H:%M}_",
            "",
            f"**Goal:** {goal or '(none specified)'}",
            f"**Files:** {', '.join(files)}",
            "",
            "## Metrics",
            "```",
            metrics or "(none)",
            "```",
            "",
            "## Analysis",
            analysis,
            "",
            "## Growth Plan (reviewed)",
            plan,
            "",
        ]
    )


if __name__ == "__main__":
    app()
