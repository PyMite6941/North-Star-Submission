"""clubs — a lightweight club hub: discover/create clubs, join, and post events.

Clubs and events live in the shared vector store, so club discovery gets semantic search
("science / coding / volunteering") for free, and the interpreter can recommend clubs.
"""

from clubs.service import add_event, create_club, join_club, list_clubs, list_events, search_clubs

__all__ = ["create_club", "list_clubs", "search_clubs", "join_club", "add_event", "list_events"]
