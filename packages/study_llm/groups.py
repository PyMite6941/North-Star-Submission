"""Offline Study Packs — bundle multiple decks/quizzes/notes into one portable file.

No server, no account: a Study Pack is a single JSON file a study group can hand around
by USB drive, AirDrop, email, or any messaging app, then each member imports it locally
and re-exports whatever they need (Anki deck, printable quiz) on their own device.
"""

from __future__ import annotations

from pathlib import Path

from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

from study_llm.flashcards import Deck, generate_deck
from study_llm.quiz import Quiz

logger = get_logger(__name__)


class StudyPack(BaseModel):
    """A portable bundle of study material a group can share as a single file."""

    name: str = Field(description="What the group is studying / the pack's title.")
    notes: str = Field(default="", description="Free-form shared notes for the group.")
    decks: list[Deck] = Field(default_factory=list)
    quizzes: list[Quiz] = Field(default_factory=list)


def build_pack(
    name: str, topics: list[str], cards_per_deck: int = 10, notes: str = ""
) -> StudyPack:
    """Generate one deck per topic (e.g. one per group member's assigned subtopic) and
    bundle them into a single :class:`StudyPack`."""
    decks = [generate_deck(topic, count=cards_per_deck) for topic in topics]
    logger.info("Built study pack %r with %d decks", name, len(decks))
    return StudyPack(name=name, notes=notes, decks=decks)


def export_pack(pack: StudyPack, path: str | Path) -> Path:
    """Write the pack as a single portable JSON file. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pack.model_dump_json(indent=2), encoding="utf-8")
    logger.info(
        "Exported study pack %r (%d decks, %d quizzes) → %s",
        pack.name,
        len(pack.decks),
        len(pack.quizzes),
        path,
    )
    return path


def import_pack(path: str | Path) -> StudyPack:
    """Load a Study Pack from a portable JSON file."""
    path = Path(path)
    pack = StudyPack.model_validate_json(path.read_text(encoding="utf-8"))
    logger.info(
        "Imported study pack %r (%d decks, %d quizzes) from %s",
        pack.name,
        len(pack.decks),
        len(pack.quizzes),
        path,
    )
    return pack


class PlayerResult(BaseModel):
    """One player's result in a pass-the-device Group Quiz."""

    name: str
    score: int
    total: int


def leaderboard(results: list[PlayerResult]) -> list[PlayerResult]:
    """Rank players by score (desc); ties broken alphabetically for a stable order."""
    return sorted(results, key=lambda r: (-r.score, r.name))
