"""College-deadline calendar export — plain RFC 5545 text, no external library.

Mirrors `fitness_agents/schedule.py`'s `.ics` writer so deadlines show up in any
calendar app (Google, Apple, Outlook) without a Polaris account of any kind.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from college_planner.models import CollegeEntry


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def export_deadlines_ics(colleges: list[CollegeEntry], path: str | Path) -> Path:
    """Write each college's deadline as an all-day event. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Polaris//College//EN",
        "CALSCALE:GREGORIAN",
    ]
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    dated = [c for c in colleges if c.deadline is not None]
    for i, c in enumerate(dated):
        day = c.deadline.strftime("%Y%m%d")
        summary = f"{c.name} application deadline"
        if c.app_type:
            summary += f" ({c.app_type})"
        lines += [
            "BEGIN:VEVENT",
            f"UID:polaris-college-{stamp}-{i}@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{day}",
            f"DTEND;VALUE=DATE:{day}",
            f"SUMMARY:{_ics_escape(summary)}",
        ]
        if c.notes:
            lines.append(f"DESCRIPTION:{_ics_escape(c.notes)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")

    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return path
