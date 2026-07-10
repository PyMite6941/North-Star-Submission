"""Structured quiz generation + grading.

Generates a typed quiz (so it renders and grades reliably) and grades a learner's
answers with per-question feedback — turning the Quizzing area into a real study loop.
Also exports to a printable Markdown handout, questions separate from the answer key, for
a study group without a device each.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import structured
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class QuizQuestion(BaseModel):
    """A single quiz question (multiple-choice if `options` is non-empty)."""

    question: str = Field(description="The question text.")
    options: list[str] = Field(
        default_factory=list,
        description="Choices for multiple-choice; leave empty for short-answer.",
    )
    answer: str = Field(description="The correct answer.")
    explanation: str = Field(description="A brief explanation of the correct answer.")


class Quiz(BaseModel):
    topic: str = Field(description="The quiz topic.")
    questions: list[QuizQuestion] = Field(description="The questions.")


class GradedAnswer(BaseModel):
    correct: bool = Field(description="Whether the learner's answer is correct.")
    feedback: str = Field(description="Short, encouraging feedback.")


class GradeResult(BaseModel):
    results: list[GradedAnswer] = Field(description="One result per question, in order.")


def generate_quiz(topic: str, count: int = 5, difficulty: str = "medium") -> Quiz:
    """Generate a `count`-question quiz on `topic` at the given difficulty."""
    system = (
        "You are a quiz master. Create clear, well-formed quiz questions (mix of multiple "
        "choice and short answer) at the requested difficulty. Provide the correct answer and "
        "a brief explanation for each."
    )
    prompt = f"Create exactly {count} {difficulty}-difficulty questions on: {topic}"
    quiz = structured(Quiz, temperature=0.4, allow_cloud=True).invoke(
        [SystemMessage(content=system), HumanMessage(content=prompt)]
    )
    if not quiz.topic:
        quiz = quiz.model_copy(update={"topic": topic})
    logger.info("Generated %d questions on %r", len(quiz.questions), topic)
    return quiz


def grade_quiz(quiz: Quiz, answers: list[str]) -> list[GradedAnswer]:
    """Grade a learner's answers (handles short-answer via the LLM). One call, all questions."""
    lines = []
    for i, q in enumerate(quiz.questions):
        given = answers[i] if i < len(answers) else ""
        lines.append(
            f"Q{i + 1}: {q.question}\nCorrect: {q.answer}\nLearner answered: {given or '(blank)'}"
        )
    system = (
        "You grade quiz answers. For each item decide if the learner's answer is correct "
        "(accept equivalent phrasings / correct option letters). Give short feedback. "
        "Return one result per question, in order."
    )
    result = structured(GradeResult, temperature=0.0, allow_cloud=True).invoke(
        [SystemMessage(content=system), HumanMessage(content="\n\n".join(lines))]
    )
    # Pad/truncate defensively so callers can always zip with questions.
    graded = list(result.results)
    while len(graded) < len(quiz.questions):
        graded.append(GradedAnswer(correct=False, feedback="(not graded)"))
    return graded[: len(quiz.questions)]


def to_markdown(quiz: Quiz) -> str:
    """Render a printable handout: questions first, then a separate answer key —
    so a study group can quiz each other from the same page without seeing answers."""
    lines: list[str] = [f"# Quiz — {quiz.topic}", ""]
    for i, q in enumerate(quiz.questions, 1):
        lines.append(f"**{i}.** {q.question}")
        for j, opt in enumerate(q.options):
            lines.append(f"   {chr(97 + j)}) {opt}")
        lines.append("")

    lines += ["---", "", "## Answer key", ""]
    for i, q in enumerate(quiz.questions, 1):
        lines.append(f"**{i}.** {q.answer} — {q.explanation}")

    return "\n".join(lines) + "\n"


def export_markdown(quiz: Quiz, path: str | Path) -> Path:
    """Write the quiz as a printable Markdown handout. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(quiz), encoding="utf-8")
    logger.info("Exported %d questions → %s", len(quiz.questions), path)
    return path
