"""Structured flashcard generation + export.

Uses the LLM's structured-output mode to produce a typed deck (not free text), so the
result is reliable to render and export. Exports to a plain Anki-importable CSV or a
double-click-importable Anki `.apkg` package — either way, usable in Anki with no North
Star install on the other end.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import genanki
from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)

# Fixed model id so every North Star deck uses the same Anki note type.
_ANKI_MODEL = genanki.Model(
    1607392319,
    "North Star Basic",
    fields=[{"name": "Question"}, {"name": "Answer"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
        }
    ],
)


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


def _stable_deck_id(topic: str) -> int:
    """Derive a stable Anki deck id from the topic, so re-exporting the same topic
    updates the same Anki deck instead of creating a duplicate."""
    digest = hashlib.sha1(f"north-star:{topic}".encode()).hexdigest()
    return int(digest[:8], 16)


def export_apkg(deck: Deck, path: str | Path) -> Path:
    """Write the deck as a double-click-importable Anki `.apkg` package. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    anki_deck = genanki.Deck(_stable_deck_id(deck.topic), deck.topic or "North Star Deck")
    for card in deck.cards:
        anki_deck.add_note(genanki.Note(model=_ANKI_MODEL, fields=[card.question, card.answer]))
    genanki.Package(anki_deck).write_to_file(str(path))
    logger.info("Exported %d cards → %s (.apkg)", len(deck.cards), path)
    return path


def export_deck(deck: Deck, path: str | Path) -> Path:
    """Export the deck, choosing the format from `path`'s suffix (`.apkg` or `.csv`)."""
    path = Path(path)
    if path.suffix.lower() == ".apkg":
        return export_apkg(deck, path)
    return export_csv(deck, path)
