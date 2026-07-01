"""Graph state for the study LLM."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from polaris_core.polaris import PolarisArea


class StudyState(TypedDict, total=False):
    """State threaded through the study graph.

    - ``messages``: the running conversation (reducer appends).
    - ``area``: the area chosen by the router for the latest turn.
    - ``area_reason``: short rationale from the router (useful for debugging/UX).
    """

    messages: Annotated[list, add_messages]
    area: PolarisArea
    area_reason: str
