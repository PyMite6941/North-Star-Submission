"""The 6 areas of Polaris fulfilled by the local study LLM (component 1).

Defined in ``root.md``:
    Flashcard Creation · Quizzing · CV Builder · Advisor · Citation Generator · Essay Helper

This module is the single source of truth for the areas: the router classifies a
request into one of these, and each has a focused handler node in ``study_llm``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PolarisArea(StrEnum):
    """The six capability areas. The string values are stable routing keys."""

    FLASHCARDS = "flashcards"
    QUIZZING = "quizzing"
    CV_BUILDER = "cv_builder"
    ADVISOR = "advisor"
    CITATION = "citation"
    ESSAY = "essay"


@dataclass(frozen=True)
class AreaInfo:
    """Metadata + the system prompt that specializes the LLM for an area."""

    area: PolarisArea
    title: str
    description: str
    system_prompt: str


POLARIS_AREAS: dict[PolarisArea, AreaInfo] = {
    PolarisArea.FLASHCARDS: AreaInfo(
        area=PolarisArea.FLASHCARDS,
        title="Flashcard Creation",
        description="Turn study material into clear question/answer flashcards.",
        system_prompt=(
            "You are a flashcard-creation expert. Convert the user's material into "
            "concise, atomic Q/A flashcards (one fact per card). Prefer active recall. "
            "Return a numbered list of 'Q:' / 'A:' pairs. Keep answers short and precise."
        ),
    ),
    PolarisArea.QUIZZING: AreaInfo(
        area=PolarisArea.QUIZZING,
        title="Quizzing",
        description="Generate quizzes and grade answers with feedback.",
        system_prompt=(
            "You are a quiz master. Create well-formed quiz questions (mix of multiple "
            "choice and short answer) at an appropriate difficulty. Always provide an "
            "answer key with brief explanations. If the user supplies answers, grade them "
            "and give targeted, encouraging feedback."
        ),
    ),
    PolarisArea.CV_BUILDER: AreaInfo(
        area=PolarisArea.CV_BUILDER,
        title="CV Builder",
        description="Draft and refine a CV / résumé.",
        system_prompt=(
            "You are a professional CV/résumé writer. Produce strong, ATS-friendly content "
            "with action verbs and quantified impact. Ask for missing essentials only when "
            "necessary; otherwise draft with sensible placeholders the user can fill in. "
            "Use clear sections: Summary, Experience, Education, Skills, Projects."
        ),
    ),
    PolarisArea.ADVISOR: AreaInfo(
        area=PolarisArea.ADVISOR,
        title="Advisor",
        description="General study and academic advice and planning.",
        system_prompt=(
            "You are a thoughtful academic advisor. Give practical, specific, and honest "
            "guidance on studying, course/subject planning, and learning strategies. "
            "Offer concrete next steps and, where useful, a simple study schedule."
        ),
    ),
    PolarisArea.CITATION: AreaInfo(
        area=PolarisArea.CITATION,
        title="Citation Generator",
        description="Produce citations in APA / MLA / Chicago.",
        system_prompt=(
            "You are a citation generator. Produce correctly formatted citations. Default "
            "to APA unless the user specifies MLA or Chicago. If source details are missing, "
            "ask for the minimum needed (author, title, year, publisher/URL) or use clearly "
            "marked placeholders. Provide both the full reference and an in-text citation."
        ),
    ),
    PolarisArea.ESSAY: AreaInfo(
        area=PolarisArea.ESSAY,
        title="Essay Helper",
        description="Outline, draft, and improve essays.",
        system_prompt=(
            "You are an essay-writing coach. Help outline, draft, and revise essays with a "
            "clear thesis, structured paragraphs, and strong transitions. When improving "
            "existing text, explain the key changes briefly. Never fabricate sources; flag "
            "claims that need a citation."
        ),
    ),
}


def area_info(area: PolarisArea) -> AreaInfo:
    """Return the :class:`AreaInfo` for an area."""
    return POLARIS_AREAS[area]


def area_catalog() -> str:
    """Human-readable catalog used in the router prompt."""
    return "\n".join(
        f"- {info.area.value}: {info.title} — {info.description}"
        for info in POLARIS_AREAS.values()
    )
