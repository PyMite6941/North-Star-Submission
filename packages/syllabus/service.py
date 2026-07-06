"""Extract + persist syllabus data into the vector store."""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core import store
from polaris_core.documents import read_file
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger

from syllabus.models import ExtractedSyllabus

logger = get_logger(__name__)

_SYSTEM = (
    "You extract structured data from a course syllabus. Identify the course (name, code, "
    "instructor, term) and every graded item (assignments, quizzes, exams, projects) with its "
    "due date (ISO YYYY-MM-DD when determinable) and grade weight percent when stated. "
    "Return only what the syllabus supports; use null for unknowns."
)


def import_syllabus_text(text: str) -> ExtractedSyllabus:
    """Parse raw syllabus text into a structured, persisted :class:`ExtractedSyllabus`."""
    llm = get_chat_model(temperature=0.0, allow_cloud=True)
    extracted = llm.with_structured_output(ExtractedSyllabus).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=text[:12000])]
    )
    _persist(extracted)
    logger.info("Imported %r (%d assignments)", extracted.course.name, len(extracted.assignments))
    return extracted


def import_syllabus_file(path: str | Path) -> ExtractedSyllabus:
    """Read a syllabus file (.pdf/.docx/.pptx/.md/.txt) and import it."""
    text = read_file(path)
    if not text or not text.strip():
        raise ValueError(f"Could not read any text from {path}")
    return import_syllabus_text(text)


def _persist(extracted: ExtractedSyllabus) -> None:
    course = extracted.course
    course_id = store.put(
        "course",
        text=f"{course.name} {course.code or ''} {course.instructor or ''}".strip(),
        meta=course.model_dump(),
        id=f"course:{_slug(course.name)}",
    )
    for a in extracted.assignments:
        store.put(
            "assignment",
            text=f"{a.title} ({a.type}) for {course.name}",
            meta={**a.model_dump(), "course": course.name, "course_id": course_id},
        )


def list_courses() -> list[dict]:
    return store.all("course")


def list_assignments(course: str | None = None) -> list[dict]:
    return store.all("assignment", where={"course": course} if course else None)


def _slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")[:40]
