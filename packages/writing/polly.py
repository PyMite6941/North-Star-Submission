"""Polly — the online AI writing coach for Polaris Student (free).

Beyond the deterministic rule checker, Polly reads the whole piece and points out, in plain
language, **where** the writing needs work — both fixes (grammar/clarity) and, importantly,
**what to add** (a missing thesis, evidence, a transition, a conclusion) — and **why**.
It can also rewrite the full text. Powered by the local/free model (no paywall).
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model, structured
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class CoachNote(BaseModel):
    """One piece of located, explained feedback."""

    kind: str = Field(description="'fix' (something wrong) or 'add' (missing content).")
    anchor: str = Field(
        description="A short verbatim quote (3–8 words) from the text marking where this "
        "applies, or 'overall' for whole-document feedback."
    )
    issue: str = Field(description="What needs to be fixed or added, briefly.")
    why: str = Field(description="Why it matters — the reason, in one sentence.")
    suggestion: str = Field(default="", description="A concrete suggested change, if any.")


class CoachReport(BaseModel):
    summary: str = Field(description="One or two sentences of overall assessment.")
    notes: list[CoachNote] = Field(description="Located fix/add feedback items.")


_SYSTEM = (
    "You are Polly, a supportive but honest writing coach for a student. Review the text and "
    "produce located, explained feedback. Include BOTH:\n"
    "  • 'fix' notes — grammar, clarity, wordiness, weak arguments;\n"
    "  • 'add' notes — MISSING content the piece needs (a clear thesis, supporting evidence, a "
    "counterargument, transitions, a concluding sentence, definitions, examples).\n"
    "For each note give a short verbatim 'anchor' quote showing where it applies (or 'overall'), "
    "what to change, and WHY it matters. Be specific and constructive; never invent facts."
)


def coach(text: str) -> CoachReport:
    """Return Polly's located fix/add feedback with reasons (structured)."""
    report = structured(CoachReport, temperature=0.2, allow_cloud=True).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=text)]
    )
    logger.info("Polly produced %d notes", len(report.notes))
    return report


_TONES = {
    "neutral": "clear and natural",
    "formal": "formal and academic",
    "friendly": "warm and approachable",
    "concise": "as concise as possible without losing meaning",
}


def polish(text: str, tone: str = "neutral") -> str:
    """Rewrite the whole text for grammar, clarity, and tone. Returns the rewrite only."""
    style = _TONES.get(tone, _TONES["neutral"])
    system = (
        "You are Polly, a professional copy editor. Rewrite the user's text to fix grammar, "
        "spelling, and punctuation, improve clarity and flow, remove wordiness, and make it "
        f"{style}. Preserve the meaning and voice. Do NOT add new facts. "
        "Return ONLY the rewritten text, no commentary."
    )
    llm = get_chat_model(temperature=0.3, allow_cloud=True)
    return llm.invoke([SystemMessage(content=system), HumanMessage(content=text)]).content.strip()
