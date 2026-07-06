"""FastAPI router for pomodoro sessions."""

from __future__ import annotations

from fastapi import APIRouter

from pomodoro.service import focus_stats, log_session

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post("/session")
def session(payload: dict) -> dict:
    """Log a completed session (JSON: {"minutes": 25, "task": "..."})."""
    rid = log_session(int(payload.get("minutes", 25)), task=payload.get("task", ""))
    return {"id": rid, **focus_stats()}


@router.get("/stats")
def stats() -> dict:
    return focus_stats()
