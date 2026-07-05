"""Club hub logic over the shared vector store."""

from __future__ import annotations

from polaris_core import store
from polaris_core.logging import get_logger

logger = get_logger(__name__)


def create_club(name: str, category: str = "", description: str = "") -> dict:
    cid = store.put(
        "club",
        text=f"{name}. {category}. {description}",
        meta={"name": name, "category": category, "description": description, "members": 0},
        id=f"club:{_slug(name)}",
    )
    return store.get(cid)  # type: ignore[return-value]


def list_clubs() -> list[dict]:
    return sorted(store.all("club"), key=lambda c: c.get("name", ""))


def search_clubs(query: str, k: int = 8) -> list[dict]:
    return store.search("club", query, k=k)


def join_club(club_id: str) -> dict:
    club = store.get(club_id)
    if not club:
        raise ValueError(f"No club {club_id}")
    members = int(club.get("members", 0)) + 1
    meta = {k: v for k, v in club.items() if k not in {"id", "text", "updated_at", "kind"}}
    meta["members"] = members
    store.put("club", text=club.get("text", club.get("name", "")), meta=meta, id=club_id)
    return {**meta, "id": club_id}


def add_event(club_id: str, title: str, when: str = "", location: str = "") -> dict:
    club = store.get(club_id)
    club_name = club.get("name") if club else club_id
    eid = store.put(
        "club_event",
        text=f"{title} — {club_name} @ {location} {when}",
        meta={
            "club_id": club_id,
            "club": club_name,
            "title": title,
            "when": when,
            "location": location,
        },
    )
    return store.get(eid)  # type: ignore[return-value]


def list_events(club_id: str | None = None) -> list[dict]:
    events = store.all("club_event", where={"club_id": club_id} if club_id else None)
    return sorted(events, key=lambda e: e.get("when", ""))


def seed_default_clubs() -> int:
    """Seed a few starter clubs on first run (idempotent by fixed ids)."""
    defaults = [
        ("Robotics Club", "STEM", "Build and compete with robots; weekly builds and outreach."),
        ("Debate Society", "Humanities", "Practice argumentation and compete in tournaments."),
        ("Coding Club", "STEM", "Hackathons, projects, and peer code review."),
        ("Volunteer Corps", "Service", "Local service events and community projects."),
        ("Art & Design", "Arts", "Studio time, portfolio nights, and exhibitions."),
    ]
    existing = {c["id"] for c in store.all("club")}
    added = 0
    for name, cat, desc in defaults:
        if f"club:{_slug(name)}" not in existing:
            create_club(name, cat, desc)
            added += 1
    if added:
        logger.info("Seeded %d default clubs", added)
    return added


def _slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")[:40]
