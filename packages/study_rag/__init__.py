"""study_rag — local, offline-capable retrieval-augmented study agents.

Ingest notes into a local Chroma vector DB, then answer study questions with
cited, retrieval-grounded responses via a corrective-RAG LangGraph.
"""

from study_rag.graph import build_graph
from study_rag.ingest import ingest_path
from study_rag.store import get_vectorstore

__all__ = ["build_graph", "ingest_path", "get_vectorstore"]
