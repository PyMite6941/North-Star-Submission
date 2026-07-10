"""Structured weekly training schedule + calendar (.ics) export.

Turns a goal (and optional analysis context) into a typed weekly plan via the LLM's
structured-output mode, then exports it as an importable iCalendar file — no external
calendar library needed (plain RFC 5545 text).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import structured
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)

_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class Workout(BaseModel):
    """A single scheduled session."""

    day: str = Field(description="Day of week, e.g. 'Monday'.")
    title: str = Field(description="Short session name, e.g. 'Tempo run'.")
    description: str = Field(description="What to do, including intensity and duration/distance.")
    duration_min: int = Field(default=45, description="Approx duration in minutes.")


class WeeklySchedule(BaseModel):
    """One week of training."""

    goal: str = Field(description="The goal this week serves.")
    workouts: list[Workout] = Field(description="Sessions for the week (rest days may be omitted).")


_SYSTEM = (
    "You are a strength-and-conditioning coach. Produce a realistic ONE-WEEK training "
    "schedule as structured data with a workout for MOST days of the week — typically 4 to 6 "
    "sessions across different weekdays (e.g. Monday, Tuesday, Thursday, Saturday, Sunday), "
    "varying intensity (easy/tempo/intervals/long/strength). Leave 1–2 days as rest by omitting "
    "them. Each workout needs a distinct day, a title, a description with intensity + "
    "duration/distance, and duration_min. Keep progression safe."
)


def generate_schedule(goal: str, context: str = "") -> WeeklySchedule:
    """Generate a typed one-week schedule for `goal`, optionally grounded in `context`."""
    context_block = f"Context:\n{context}\n\n" if context else ""
    prompt = f"Goal: {goal}\n\n{context_block}Build the week."
    schedule = structured(WeeklySchedule, temperature=0.3, allow_cloud=True).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=prompt)]
    )
    if not schedule.goal:
        schedule = schedule.model_copy(update={"goal": goal})
    logger.info("Generated %d workouts for %r", len(schedule.workouts), goal)
    return schedule


def _next_date_for(day_name: str, start: date) -> date:
    """The first date on/after `start` matching the given weekday name."""
    try:
        target = _WEEKDAYS.index(day_name.strip().capitalize())
    except ValueError:
        return start  # unknown day → schedule at start
    delta = (target - start.weekday()) % 7
    return start + timedelta(days=delta)


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def export_ics(schedule: WeeklySchedule, path: str | Path, start: date | None = None) -> Path:
    """Write the schedule to an .ics file (importable into any calendar app)."""
    start = start or date.today()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Polaris//Fitness//EN",
        "CALSCALE:GREGORIAN",
    ]
    for i, w in enumerate(schedule.workouts):
        day = _next_date_for(w.day, start)
        # All-day-ish morning slot at 07:00 local, duration as specified.
        begin = datetime(day.year, day.month, day.day, 7, 0)
        end = begin + timedelta(minutes=max(1, w.duration_min))
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        lines += [
            "BEGIN:VEVENT",
            f"UID:polaris-{stamp}-{i}@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{begin:%Y%m%dT%H%M%S}",
            f"DTEND:{end:%Y%m%dT%H%M%S}",
            f"SUMMARY:{_ics_escape(w.title)}",
            f"DESCRIPTION:{_ics_escape(w.description)}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")

    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    logger.info("Exported %d events → %s", len(schedule.workouts), path)
    return path
