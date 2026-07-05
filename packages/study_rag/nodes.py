"""Nodes for the corrective-RAG study graph."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.config import get_settings
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

from study_rag.state import RagState
from study_rag.store import get_vectorstore

logger = get_logger(__name__)


def retrieve(state: RagState) -> dict:
    """Fetch the top-k chunks for the current question from Chroma."""
    settings = get_settings()
    store = get_vectorstore(settings)
    docs = store.similarity_search(state["question"], k=settings.rag_top_k)
    logger.info("Retrieved %d chunks for: %s", len(docs), state["question"])
    return {"documents": docs, "attempts": state.get("attempts", 0) + 1}


class _Grade(BaseModel):
    relevant: bool = Field(description="Do the documents contain info to answer the question?")


def grade_docs(state: RagState) -> dict:
    """Judge whether retrieved context is good enough to answer."""
    docs = state.get("documents", [])
    if not docs:
        return {"relevant": False}
    context = "\n\n".join(d.page_content[:500] for d in docs)
    llm = get_chat_model(temperature=0.0)
    prompt = (
        "Question:\n"
        f"{state['question']}\n\nRetrieved context:\n{context}\n\n"
        "Does the context contain information needed to answer the question?"
    )
    try:
        grade = llm.with_structured_output(_Grade).invoke(
            [SystemMessage(content="You grade retrieval quality."), HumanMessage(content=prompt)]
        )
        relevant = grade.relevant
    except Exception as exc:  # noqa: BLE001 - assume usable on grader failure
        logger.warning("Grader failed (%s); assuming relevant.", exc)
        relevant = True
    logger.info("Docs relevant: %s", relevant)
    return {"relevant": relevant}


def rewrite_query(state: RagState) -> dict:
    """Reformulate the question to improve retrieval, then loop back."""
    llm = get_chat_model(temperature=0.3)
    original = state.get("original_question", state["question"])
    prompt = (
        f"Rewrite this study question to be clearer and richer in keywords for "
        f"document retrieval. Return only the rewritten question.\n\n{original}"
    )
    new_q = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    logger.info("Rewrote query → %s", new_q)
    return {"question": new_q}


def generate(state: RagState) -> dict:
    """Produce a cited answer grounded in the retrieved context."""
    docs = state.get("documents", [])
    llm = get_chat_model()
    if not docs:
        # No grounding available — answer honestly without fabricating sources.
        msg = (
            "You are a study assistant. No relevant notes were found. Answer from general "
            "knowledge if you can, and clearly state that this is not grounded in the user's notes."
        )
        answer = llm.invoke(
            [SystemMessage(content=msg), HumanMessage(content=state["question"])]
        ).content
        return {"answer": answer}

    numbered = "\n\n".join(
        f"[{i + 1}] (source: {d.metadata.get('source', '?')})\n{d.page_content}"
        for i, d in enumerate(docs)
    )
    system = (
        "You are a study assistant. Answer ONLY using the numbered context below. "
        "Cite sources inline like [1], [2]. If the context is insufficient, say so. "
        "Do not invent facts.\n\nContext:\n" + numbered
    )
    answer = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=state["original_question"])]
    ).content
    return {"answer": answer}


# --- conditional edge ---
def decide_after_grade(state: RagState) -> str:
    """Route to generation if docs are good or we're out of attempts; else rewrite."""
    max_attempts = get_settings().rag_max_attempts
    if state.get("relevant") or state.get("attempts", 0) >= max_attempts:
        return "generate"
    return "rewrite_query"
