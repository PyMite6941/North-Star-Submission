"""Workload detection: bucket upcoming assignments by week and score intensity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from polaris_core import store
from polaris_core.logging import get_logger

logger = get_logger(__name__)

# Effort weight per assignment type (relative units) when no grade weight is given.
_TYPE_EFFORT = {"exam": 5.0, "project": 4.0, "quiz": 2.0, "assignment": 2.0, "reading": 1.0}


@dataclass
class WeekLoad:
    week_start: str  # ISO Monday date
    items: list[dict] = field(default_factory=list)
    score: float = 0.0
    heavy: bool = False


def _parse_date(v) -> date | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v)).date()
    except ValueError:
        return None


def _effort(item: dict) -> float:
    w = item.get("weight_pct")
    if isinstance(w, (int, float)) and w > 0:
        return 1.0 + float(w) / 10.0  # heavier weighting = more effort
    return _TYPE_EFFORT.get(str(item.get("type", "assignment")).lower(), 2.0)


def detect_workload(heavy_threshold: float | None = None) -> list[WeekLoad]:
    """Group assignments with due dates into ISO weeks and flag heavy ones.

    A week is "heavy" when its score exceeds ``heavy_threshold`` (default: 1.6× the mean
    non-empty week, so it adapts to each student's load).
    """
    assignments = store.all("assignment")
    by_week: dict[date, WeekLoad] = {}
    for a in assignments:
        d = _parse_date(a.get("due_date"))
        if not d:
            continue
        monday = date.fromordinal(d.toordinal() - d.weekday())
        wk = by_week.setdefault(monday.isoformat(), WeekLoad(week_start=monday.isoformat()))  # type: ignore[arg-type]
        wk.items.append(a)
        wk.score += _effort(a)

    weeks = sorted(by_week.values(), key=lambda w: w.week_start)
    if weeks:
        mean = sum(w.score for w in weeks) / len(weeks)
        threshold = heavy_threshold if heavy_threshold is not None else mean * 1.6
        for w in weeks:
            w.heavy = w.score >= threshold and w.score > 0
    logger.info("Workload across %d weeks", len(weeks))
    return weeks
