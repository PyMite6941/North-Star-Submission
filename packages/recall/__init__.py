"""recall — free, Quizlet-style active-recall flashcards with spaced repetition.

Decks and cards live in the shared vector store; each card carries its SM-2 scheduling
state (ease, interval, due date) in metadata. Cards can be typed in or AI-generated
(reusing ``study_llm.flashcards``). The review endpoint serves due cards and updates
their schedule from your grade — the core of durable, free active recall.
"""

from recall.service import (
    add_card,
    create_deck,
    due_cards,
    generate_deck,
    list_decks,
    review_card,
)
from recall.sm2 import SM2State, schedule

__all__ = [
    "create_deck",
    "generate_deck",
    "add_card",
    "list_decks",
    "due_cards",
    "review_card",
    "SM2State",
    "schedule",
]
