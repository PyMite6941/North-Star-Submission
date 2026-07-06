"""FastAPI router for spaced-repetition recall."""

from __future__ import annotations

from fastapi import APIRouter

from recall.service import add_card, create_deck, due_cards, generate_deck, list_decks, review_card

router = APIRouter(prefix="/recall", tags=["recall"])


@router.get("/decks")
def decks() -> list[dict]:
    return list_decks()


@router.post("/decks")
def make_deck(payload: dict) -> dict:
    """Create a deck. With {"topic": "..."} the cards are AI-generated."""
    name = payload["name"]
    if payload.get("topic"):
        return generate_deck(name, payload["topic"], int(payload.get("count", 10)))
    return create_deck(name, payload.get("description", ""))


@router.post("/decks/{deck_id}/cards")
def create_card(deck_id: str, payload: dict) -> dict:
    return add_card(deck_id, payload["question"], payload["answer"])


@router.get("/review")
def review_queue(deck_id: str | None = None) -> list[dict]:
    """Cards due for review now (optionally scoped to a deck)."""
    return due_cards(deck_id)


@router.post("/review/{card_id}")
def grade(card_id: str, payload: dict) -> dict:
    """Grade a reviewed card (JSON: {"grade": 0-5})."""
    return review_card(card_id, int(payload.get("grade", 3)))
