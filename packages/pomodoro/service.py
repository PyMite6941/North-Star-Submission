"""Pomodoro session logging + focus statistics."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from polaris_core import store
from polaris_core.logging import get_logger

logger = get_logger(__name__)


def log_session(minutes: int, task: str = "", when: datetime | None = None) -> str:
    """Record a completed focus session. Returns its id."""
    when = when or datetime.now()
    return store.put(
        "pomodoro",
        text=f"Focused {minutes} min on {task or 'study'}",
        meta={
            "minutes": int(minutes),
            "task": task,
            "date": when.date().isoformat(),
            "ts": when.isoformat(),
        },
    )


def focus_stats() -> dict:
    """Total focus minutes, sessions, today's minutes, and current day-streak."""
    sessions = store.all("pomodoro")
    if not sessions:
        return {"sessions": 0, "total_minutes": 0, "today_minutes": 0, "streak_days": 0}

    total = sum(int(s.get("minutes", 0)) for s in sessions)
    days = {s.get("date") for s in sessions if s.get("date")}
    today = date.today()
    today_iso = today.isoformat()
    today_min = sum(int(s.get("minutes", 0)) for s in sessions if s.get("date") == today_iso)

    # Current streak: consecutive days ending today (or yesterday) with a session.
    streak = 0
    cur = today
    if today_iso not in days and (today - timedelta(days=1)).isoformat() in days:
        cur = today - timedelta(days=1)
    while cur.isoformat() in days:
        streak += 1
        cur -= timedelta(days=1)

    return {
        "sessions": len(sessions),
        "total_minutes": total,
        "today_minutes": today_min,
        "streak_days": streak,
    }
