"""FastAPI router for the writing assistant (all endpoints free)."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/writing", tags=["writing"])


class TextRequest(BaseModel):
    text: str


class PolishRequest(BaseModel):
    text: str
    tone: str = "neutral"


@router.post("/check")
def check_text(req: TextRequest) -> dict:
    """Deterministic rule check (no AI): issues + readability + score."""
    from writing.check import check

    report = check(req.text)
    return {
        "issues": [asdict(i) for i in report.issues],
        "words": report.words,
        "sentences": report.sentences,
        "flesch_reading_ease": report.flesch_reading_ease,
        "flesch_kincaid_grade": report.flesch_kincaid_grade,
        "score": report.score,
        "counts": report.counts,
    }


@router.post("/coach")
def polly_coach(req: TextRequest) -> dict:
    """Polly (AI): where to fix and add, each with a reason."""
    from writing.polly import coach

    return coach(req.text).model_dump()


@router.post("/polish")
def polly_polish(req: PolishRequest) -> dict:
    """Polly (AI): a full clarity/grammar rewrite in the requested tone."""
    from writing.polly import polish

    return {"rewrite": polish(req.text, tone=req.tone)}
