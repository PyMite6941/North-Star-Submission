"""Nodes for the study graph: a router plus one handler per Polaris area."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from polaris_core.polaris import POLARIS_AREAS, PolarisArea, area_catalog, area_info
from pydantic import BaseModel, Field

from study_llm.state import StudyState

logger = get_logger(__name__)


class _Route(BaseModel):
    """Structured router decision."""

    area: PolarisArea = Field(description="Which Polaris area best handles this request.")
    reason: str = Field(description="One short sentence explaining the choice.")


_ROUTER_SYSTEM = (
    "You route a student's request to exactly one capability area. "
    "Choose the single best fit.\n\nAreas:\n" + area_catalog()
)


def route(state: StudyState) -> dict:
    """Classify the latest user turn into one of the 6 areas.

    If the caller already pinned an ``area`` (e.g. via ``--area``), honour it and
    skip the LLM classification entirely.
    """
    forced = state.get("area")
    if forced is not None:
        logger.info("Area pinned to %s (router skipped)", forced.value)
        return {"area": forced, "area_reason": "pinned by caller"}

    llm = get_chat_model(temperature=0.0)
    last = state["messages"][-1]
    try:
        decision = llm.with_structured_output(_Route).invoke(
            [SystemMessage(content=_ROUTER_SYSTEM), last]
        )
        area, reason = decision.area, decision.reason
    except Exception as exc:  # noqa: BLE001 - fall back to a safe default
        logger.warning("Router failed (%s); defaulting to advisor.", exc)
        area, reason = PolarisArea.ADVISOR, "fallback default"
    logger.info("Routed to %s — %s", area.value, reason)
    return {"area": area, "area_reason": reason}


def _make_handler(area: PolarisArea):
    """Build a handler node that answers with the area's specialized system prompt."""
    info = area_info(area)

    def handler(state: StudyState) -> dict:
        llm = get_chat_model()
        messages = [SystemMessage(content=info.system_prompt), *state["messages"]]
        response = llm.invoke(messages)
        return {"messages": [response]}

    handler.__name__ = f"handle_{area.value}"
    return handler


# One handler node per area, keyed by area value (used as node names in the graph).
HANDLERS = {area.value: _make_handler(area) for area in POLARIS_AREAS}
