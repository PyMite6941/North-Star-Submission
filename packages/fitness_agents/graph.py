"""Compile the fitness pipeline graph.

    START → parse_and_summarize → analyze → plan → review → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from fitness_agents.nodes import analyze, parse_and_summarize, plan, review
from fitness_agents.state import FitnessState


def build_graph(checkpointer=None):
    """Build and compile the fitness agent pipeline."""
    builder = StateGraph(FitnessState)
    builder.add_node("parse", parse_and_summarize)
    builder.add_node("analyze", analyze)
    builder.add_node("plan", plan)
    builder.add_node("review", review)

    builder.add_edge(START, "parse")
    builder.add_edge("parse", "analyze")
    builder.add_edge("analyze", "plan")
    builder.add_edge("plan", "review")
    builder.add_edge("review", END)

    return builder.compile(checkpointer=checkpointer)
