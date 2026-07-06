"""FastAPI router for syllabus import."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from syllabus.service import (
    import_syllabus_file,
    import_syllabus_text,
    list_assignments,
    list_courses,
)

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("/import-upload")
async def import_upload(file: UploadFile = File(...)) -> dict:  # noqa: B008 - FastAPI pattern
    """Import an uploaded syllabus file (PDF/DOCX/PPTX/MD/TXT)."""
    tmp = Path(tempfile.mkdtemp()) / (file.filename or "syllabus")
    tmp.write_bytes(await file.read())
    return import_syllabus_file(tmp).model_dump()


@router.post("/import-text")
def import_text(payload: dict) -> dict:
    """Import syllabus text pasted by the user (JSON: {"text": "..."})."""
    return import_syllabus_text(payload.get("text", "")).model_dump()


@router.get("/courses")
def courses() -> list[dict]:
    return list_courses()


@router.get("/assignments")
def assignments(course: str | None = None) -> list[dict]:
    return list_assignments(course)
