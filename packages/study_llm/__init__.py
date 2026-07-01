"""study_llm — the offline study LLM fulfilling the 6 areas of Polaris.

A LangGraph router classifies each request into one of the six areas and dispatches
it to a focused handler. See :func:`build_graph`.
"""

from study_llm.graph import build_graph

__all__ = ["build_graph"]
