"""FastAPI router for the club hub."""

from __future__ import annotations

from fastapi import APIRouter

from clubs.service import (
    add_event,
    create_club,
    join_club,
    list_clubs,
    list_events,
    search_clubs,
    seed_default_clubs,
)

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get("")
def clubs(q: str | None = None) -> list[dict]:
    """List clubs (seeds defaults on first call), or semantic-search with ?q=."""
    seed_default_clubs()
    return search_clubs(q) if q else list_clubs()


@router.post("")
def create(payload: dict) -> dict:
    """Create a club (JSON: {"name", "category", "description"})."""
    return create_club(payload["name"], payload.get("category", ""), payload.get("description", ""))


@router.post("/{club_id}/join")
def join(club_id: str) -> dict:
    return join_club(club_id)


@router.get("/{club_id}/events")
def events(club_id: str) -> list[dict]:
    return list_events(club_id)


@router.post("/{club_id}/events")
def create_event(club_id: str, payload: dict) -> dict:
    """Add an event (JSON: {"title", "when", "location"})."""
    return add_event(
        club_id, payload["title"], payload.get("when", ""), payload.get("location", "")
    )
