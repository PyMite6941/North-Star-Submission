"""Compile the study LLM graph: START → route → <area handler> → END."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from polaris_core.polaris import POLARIS_AREAS

from study_llm.nodes import HANDLERS, route
from study_llm.state import StudyState


def _pick_handler(state: StudyState) -> str:
    """Conditional edge: send to the node named after the chosen area."""
    return state["area"].value


def build_graph(checkpointer=None):
    """Build and compile the study graph.

    Pass a LangGraph checkpointer (see ``polaris_core.memory``) to persist
    conversations across turns by ``thread_id``.
    """
    builder = StateGraph(StudyState)
    builder.add_node("route", route)
    for name, handler in HANDLERS.items():
        builder.add_node(name, handler)

    builder.add_edge(START, "route")
    builder.add_conditional_edges(
        "route",
        _pick_handler,
        {area.value: area.value for area in POLARIS_AREAS},
    )
    for name in HANDLERS:
        builder.add_edge(name, END)

    return builder.compile(checkpointer=checkpointer)
