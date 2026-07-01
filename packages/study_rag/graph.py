"""Compile the corrective-RAG study graph.

    START → retrieve → grade_docs → (generate | rewrite_query → retrieve …) → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from study_rag.nodes import (
    decide_after_grade,
    generate,
    grade_docs,
    retrieve,
    rewrite_query,
)
from study_rag.state import RagState


def build_graph(checkpointer=None):
    """Build and compile the RAG query graph."""
    builder = StateGraph(RagState)
    builder.add_node("retrieve", retrieve)
    builder.add_node("grade_docs", grade_docs)
    builder.add_node("rewrite_query", rewrite_query)
    builder.add_node("generate", generate)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade_docs")
    builder.add_conditional_edges(
        "grade_docs",
        decide_after_grade,
        {"generate": "generate", "rewrite_query": "rewrite_query"},
    )
    builder.add_edge("rewrite_query", "retrieve")
    builder.add_edge("generate", END)

    return builder.compile(checkpointer=checkpointer)
