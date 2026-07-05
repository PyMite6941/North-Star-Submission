"""Deck + card management and review scheduling over the vector store."""

from __future__ import annotations

from datetime import date

from polaris_core import store
from polaris_core.logging import get_logger

from recall.sm2 import SM2State, schedule

logger = get_logger(__name__)


# ------------------------------------------------------------------------ decks
def create_deck(name: str, description: str = "") -> dict:
    did = store.put(
        "deck",
        text=f"{name}. {description}",
        meta={"name": name, "description": description},
        id=f"deck:{_slug(name)}",
    )
    return store.get(did)  # type: ignore[return-value]


def list_decks() -> list[dict]:
    decks = store.all("deck")
    for d in decks:
        d["cards"] = len(store.all("card", where={"deck_id": d["id"]}))
        d["due"] = len(due_cards(d["id"]))
    return sorted(decks, key=lambda d: d.get("name", ""))


def add_card(deck_id: str, question: str, answer: str) -> dict:
    st = SM2State.new()
    cid = store.put(
        "card",
        text=f"Q: {question}\nA: {answer}",
        meta={
            "deck_id": deck_id,
            "question": question,
            "answer": answer,
            "ease": st.ease,
            "interval": st.interval,
            "repetitions": st.repetitions,
            "due": st.due,
        },
    )
    return store.get(cid)  # type: ignore[return-value]


def generate_deck(name: str, topic: str, count: int = 10) -> dict:
    """AI-generate a deck's cards from a topic (reuses the study LLM flashcard generator)."""
    from study_llm.flashcards import generate_deck as gen

    deck = create_deck(name, description=f"AI-generated on {topic}")
    result = gen(topic, count=count)
    for card in result.cards:
        add_card(deck["id"], card.question, card.answer)
    logger.info("Generated deck %r with %d cards", name, len(result.cards))
    deck["cards"] = len(result.cards)
    return deck


# ----------------------------------------------------------------------- review
def due_cards(deck_id: str | None = None, today: date | None = None) -> list[dict]:
    """Cards due for review today or earlier (optionally within one deck)."""
    today = (today or date.today()).isoformat()
    where = {"deck_id": deck_id} if deck_id else None
    return [c for c in store.all("card", where=where) if str(c.get("due", "")) <= today]


def review_card(card_id: str, grade: int) -> dict:
    """Grade a card (0–5) and persist its next SM-2 schedule."""
    card = store.get(card_id)
    if not card:
        raise ValueError(f"No card {card_id}")
    state = SM2State(
        ease=float(card.get("ease", 2.5)),
        interval=int(card.get("interval", 0)),
        repetitions=int(card.get("repetitions", 0)),
        due=str(card.get("due", "")),
    )
    nxt = schedule(state, grade)
    meta = {k: v for k, v in card.items() if k not in {"id", "text", "updated_at", "kind"}}
    meta.update(ease=nxt.ease, interval=nxt.interval, repetitions=nxt.repetitions, due=nxt.due)
    store.put("card", text=card.get("text", ""), meta=meta, id=card_id)
    return {"id": card_id, **meta}


def _slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")[:40]
