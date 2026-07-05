"""Retrieve-and-interpret over the app vector store."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core import store
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM = (
    "You are Polaris, a student's study-life assistant. Answer the question using the "
    "retrieved context items (each has a kind and metadata such as due dates, weights, or "
    "review state). Be concrete and cite item titles where relevant. If the context is "
    "insufficient, say what's missing. Never invent deadlines or facts."
)


@dataclass
class Interpretation:
    answer: str
    used: list[dict]  # the retrieved items that grounded the answer


def _format(items: list[dict]) -> str:
    lines = []
    for it in items:
        meta = {k: v for k, v in it.items() if k not in {"id", "text", "updated_at"}}
        lines.append(f"[{it.get('kind', '?')}] {it.get('text', '')[:400]}  meta={meta}")
    return "\n\n".join(lines)


def interpret(question: str, kinds: list[str] | None = None, k: int = 8) -> Interpretation:
    """Answer a question by retrieving from the vector store and interpreting via the LLM.

    ``kinds`` optionally restricts which feature data to search; None searches everything.
    """
    items: list[dict] = []
    if kinds:
        per = max(2, k // len(kinds))
        for kind in kinds:
            items.extend(store.search(kind, question, k=per))
    else:
        items = store.search(None, question, k=k)

    context = _format(items) if items else "(no stored items matched)"
    llm = get_chat_model(allow_cloud=True)  # honour the free-API preference when enabled
    answer = llm.invoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Question: {question}\n\nContext:\n{context}"),
        ]
    ).content
    logger.info("Interpreted question over %d items", len(items))
    return Interpretation(answer=answer, used=items)
