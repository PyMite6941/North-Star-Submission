"""Structured flashcard generation + export.

Uses the LLM's structured-output mode to produce a typed deck (not free text), so the
result is reliable to render and export. Exports to an Anki-importable CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class Flashcard(BaseModel):
    """A single atomic flashcard."""

    question: str = Field(description="The prompt / front of the card.")
    answer: str = Field(description="The concise answer / back of the card.")


class Deck(BaseModel):
    """A set of flashcards on a topic."""

    topic: str = Field(description="The deck's topic.")
    cards: list[Flashcard] = Field(description="The flashcards.")


_SYSTEM = (
    "You are a flashcard-creation expert. Produce concise, atomic flashcards (one fact per "
    "card) suitable for spaced-repetition study. Keep answers short and precise."
)


def generate_deck(topic: str, count: int = 10) -> Deck:
    """Generate a structured deck of `count` flashcards on `topic`."""
    llm = get_chat_model(temperature=0.3)
    prompt = f"Create exactly {count} flashcards on: {topic}"
    deck = llm.with_structured_output(Deck).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=prompt)]
    )
    # Ensure the topic is populated even if the model omits it.
    if not deck.topic:
        deck = deck.model_copy(update={"topic": topic})
    logger.info("Generated %d cards on %r", len(deck.cards), topic)
    return deck


def export_csv(deck: Deck, path: str | Path) -> Path:
    """Write the deck as an Anki-importable CSV (front,back). Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        for card in deck.cards:
            writer.writerow([card.question, card.answer])
    logger.info("Exported %d cards → %s", len(deck.cards), path)
    return path
