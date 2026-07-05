"""CLI for the offline College Planner — application tracker + 4-year course map.

    polaris-college add "MIT" --deadline 2027-01-01 --type "Early Action"
    polaris-college list
    polaris-college status "MIT" submitted
    polaris-college deadlines --export deadlines.ics    # -> any calendar app
    polaris-college course add Math "AP Calculus BC" --credits 1 --year 12 --grade A
    polaris-college course list
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from polaris_core.console import console
from rich.table import Table

from college_planner.calendar_export import export_deadlines_ics
from college_planner.models import CollegeEntry, CourseEntry
from college_planner.storage import (
    add_college,
    add_course,
    list_colleges,
    list_courses,
    remove_college,
    total_credits,
    update_status,
)

app = typer.Typer(
    help="Offline college-application tracker + 4-year course map.", no_args_is_help=True
)
course_app = typer.Typer(help="Track courses toward your 4-year plan / transcript.")
app.add_typer(course_app, name="course")


@app.command("add")
def college_add(
    name: str,
    deadline: str | None = typer.Option(None, "--deadline", help="YYYY-MM-DD."),
    app_type: str = typer.Option(
        "", "--type", help="e.g. 'Early Action', 'Early Decision', 'Regular Decision'."
    ),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Add a college to your list (re-running with the same name updates it)."""
    parsed = date.fromisoformat(deadline) if deadline else None
    add_college(CollegeEntry(name=name, app_type=app_type, deadline=parsed, notes=notes))
    console.print(f"[green]✓ Saved[/] {name}")


@app.command("list")
def college_list() -> None:
    """List every college on your list, soonest deadline first."""
    table = Table(title="Your colleges")
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Deadline")
    table.add_column("Status", style="cyan")
    for c in list_colleges():
        deadline = c.deadline.isoformat() if c.deadline else "-"
        table.add_row(c.name, c.app_type or "-", deadline, c.status)
    console.print(table)


@app.command("status")
def college_status(name: str, status: str) -> None:
    """Update a college's application status."""
    if update_status(name, status):
        console.print(f"[green]✓[/] {name} → {status}")
    else:
        console.print(f"[red]No college named {name!r}. Add it first with `add`.[/]")


@app.command("remove")
def college_remove(name: str) -> None:
    """Remove a college from your list."""
    if remove_college(name):
        console.print(f"[green]✓ Removed[/] {name}")
    else:
        console.print(f"[red]No college named {name!r}.[/]")


@app.command("deadlines")
def college_deadlines(
    export: Path = typer.Option(..., "--export", "-e", help="Write deadlines as .ics here."),
) -> None:
    """Export every college's deadline as a calendar event — works in any calendar app."""
    dated = [c for c in list_colleges() if c.deadline is not None]
    path = export_deadlines_ics(dated, export)
    console.print(f"[green]✓ Exported {len(dated)} deadline(s) →[/] {path}")


@course_app.command("add")
def course_add(
    subject: str,
    course_name: str,
    credits: float = typer.Option(1.0, "--credits"),
    year: int = typer.Option(..., "--year", help="Grade level, e.g. 9-12."),
    grade: str = typer.Option("", "--grade"),
) -> None:
    """Add a course toward your 4-year plan / transcript."""
    entry = CourseEntry(
        subject=subject, course_name=course_name, credits=credits, year=year, grade=grade
    )
    add_course(entry)
    console.print(f"[green]✓ Added[/] {course_name} (year {year})")


@course_app.command("list")
def course_list() -> None:
    """List every course, grouped by year, with a running credit total."""
    table = Table(title=f"Courses — {total_credits():g} credits total")
    table.add_column("Year", justify="right")
    table.add_column("Subject")
    table.add_column("Course")
    table.add_column("Credits", justify="right")
    table.add_column("Grade")
    for c in list_courses():
        table.add_row(str(c.year), c.subject, c.course_name, f"{c.credits:g}", c.grade or "-")
    console.print(table)


if __name__ == "__main__":
    app()
