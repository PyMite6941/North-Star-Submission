"""Graph state for the RAG study agent."""

from __future__ import annotations

from typing import TypedDict

from langchain_core.documents import Document


class RagState(TypedDict, total=False):
    """State for a single corrective-RAG query run.

    - ``question``: the user's (possibly rewritten) query.
    - ``original_question``: the question as first asked.
    - ``documents``: retrieved + graded context chunks.
    - ``relevant``: whether retrieval was judged useful.
    - ``attempts``: how many retrieve/rewrite cycles have run.
    - ``answer``: the final cited answer.
    """

    question: str
    original_question: str
    documents: list[Document]
    relevant: bool
    attempts: int
    answer: str
