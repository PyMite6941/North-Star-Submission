"""FastAPI router for workload + weekly planning."""

from __future__ import annotations

from fastapi import APIRouter

from planner.service import make_weekly_plan
from planner.workload import detect_workload

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get("/workload")
def workload() -> list[dict]:
    """Per-week workload with heavy-week flags."""
    return [
        {
            "week_start": w.week_start,
            "score": round(w.score, 1),
            "heavy": w.heavy,
            "count": len(w.items),
        }
        for w in detect_workload()
    ]


@router.post("/week")
def weekly_plan(payload: dict | None = None) -> dict:
    """Build a smart weekly study plan (JSON: {"study_hours_per_day": 2})."""
    hours = float((payload or {}).get("study_hours_per_day", 2.0))
    return make_weekly_plan(study_hours_per_day=hours).model_dump()
