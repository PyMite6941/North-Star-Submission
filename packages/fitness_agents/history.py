"""Persistent training history + progress trends.

Each analyzed/logged activity is stored in a local SQLite DB so we can track
progress over time: chronic vs. acute load (fitness/fatigue/form) and PRs.
This is what turns the fitness component from a single-snapshot analyzer into a
progress tracker (the brief's "analyze a user's fitness progress").
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from polaris_core.config import get_settings
from polaris_core.logging import get_logger

from fitness_agents.metrics import _KM_PER_MI, ActivitySummary

logger = get_logger(__name__)


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(str(get_settings().fitness_path()))
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT,
            distance_km REAL,
            duration_s REAL,
            avg_hr REAL,
            training_load REAL,
            data TEXT
        )
        """
    )
    return con


def log_session(summary: ActivitySummary, source: str, when: datetime | None = None) -> int:
    """Record one activity. Returns the new row id."""
    when = when or datetime.now()
    con = _conn()
    cur = con.execute(
        "INSERT INTO sessions(date, source, distance_km, duration_s, avg_hr, training_load, data)"
        " VALUES (?,?,?,?,?,?,?)",
        (
            when.isoformat(),
            source,
            summary.distance_km,
            summary.duration_s,
            summary.avg_heart_rate,
            summary.training_load,
            summary.model_dump_json(),
        ),
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    logger.info("Logged session #%s from %s", row_id, source)
    return row_id


def list_sessions(limit: int | None = None) -> list[dict]:
    """Return stored sessions, most recent first."""
    con = _conn()
    q = "SELECT * FROM sessions ORDER BY date DESC"
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = [dict(r) for r in con.execute(q).fetchall()]
    con.close()
    return rows


def clear_history() -> None:
    """Delete all stored sessions."""
    con = _conn()
    con.execute("DELETE FROM sessions")
    con.commit()
    con.close()


@dataclass
class Trends:
    n_sessions: int
    ctl: float  # chronic training load (~fitness), 42-day EWMA
    atl: float  # acute training load (~fatigue), 7-day EWMA
    tsb: float  # training stress balance (~form) = ctl - atl
    total_distance_km: float
    last7_distance_km: float
    longest_km: float | None
    best_pace_min_per_km: float | None

    def to_prompt(self, units: str | None = None) -> str:
        """``units`` is ``"metric"`` or ``"imperial"``; defaults to ``POLARIS_UNITS``."""
        if units is None:
            from polaris_core.config import get_settings

            units = get_settings().units
        imperial = units == "imperial"

        def _dist(km: float) -> str:
            return f"{km / _KM_PER_MI:.1f} mi" if imperial else f"{km:.1f} km"

        form = "fresh" if self.tsb > 5 else "fatigued" if self.tsb < -10 else "neutral"
        lines = [
            f"- sessions logged: {self.n_sessions}",
            f"- fitness (CTL): {self.ctl:.1f}",
            f"- fatigue (ATL): {self.atl:.1f}",
            f"- form (TSB): {self.tsb:+.1f} ({form})",
            f"- total distance: {_dist(self.total_distance_km)}",
            f"- last 7 days: {_dist(self.last7_distance_km)}",
        ]
        if self.longest_km:
            lines.append(f"- longest activity: {_dist(self.longest_km)}")
        if self.best_pace_min_per_km:
            pace = self.best_pace_min_per_km
            pace_str = f"{pace * _KM_PER_MI:.2f} min/mi" if imperial else f"{pace:.2f} min/km"
            lines.append(f"- best avg pace: {pace_str}")
        return "\n".join(lines)


def compute_trends() -> Trends | None:
    """Compute fitness/fatigue/form (EWMA of daily load) and PRs from history."""
    rows = list_sessions()
    if not rows:
        return None

    # Aggregate training load by calendar day.
    by_day: dict = {}
    for r in rows:
        day = datetime.fromisoformat(r["date"]).date()
        by_day[day] = by_day.get(day, 0.0) + (r["training_load"] or 0.0)

    start, end = min(by_day), max(by_day)
    kc, ka = 2 / (42 + 1), 2 / (7 + 1)  # EWMA smoothing for 42-day / 7-day
    ctl = atl = 0.0
    day = start
    while day <= end:
        load = by_day.get(day, 0.0)
        ctl += kc * (load - ctl)
        atl += ka * (load - atl)
        day += timedelta(days=1)

    total_km = sum(r["distance_km"] or 0.0 for r in rows)
    cutoff = datetime.now() - timedelta(days=7)
    last7 = sum(
        (r["distance_km"] or 0.0)
        for r in rows
        if datetime.fromisoformat(r["date"]) >= cutoff
    )
    dists = [r["distance_km"] for r in rows if r["distance_km"]]
    paces = [
        (r["duration_s"] / 60) / r["distance_km"]
        for r in rows
        if r["distance_km"] and r["duration_s"]
    ]

    return Trends(
        n_sessions=len(rows),
        ctl=ctl,
        atl=atl,
        tsb=ctl - atl,
        total_distance_km=total_km,
        last7_distance_km=last7,
        longest_km=max(dists) if dists else None,
        best_pace_min_per_km=min(paces) if paces else None,
    )
