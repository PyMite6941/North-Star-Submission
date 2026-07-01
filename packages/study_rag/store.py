"""Chroma vector store wrapper (embedded, persists to local disk)."""

from __future__ import annotations

from langchain_chroma import Chroma
from polaris_core.config import Settings, get_settings
from polaris_core.embeddings import get_embeddings


def get_vectorstore(settings: Settings | None = None) -> Chroma:
    """Return the persistent Chroma collection for study notes."""
    settings = settings or get_settings()
    return Chroma(
        collection_name=settings.rag_collection,
        embedding_function=get_embeddings(settings),
        persist_directory=str(settings.chroma_path()),
    )


def collection_count(settings: Settings | None = None) -> int:
    """Number of chunks currently stored in the collection."""
    store = get_vectorstore(settings)
    try:
        return store._collection.count()
    except Exception:  # noqa: BLE001 - empty/new collection
        return 0


def reset_collection(settings: Settings | None = None) -> None:
    """Delete all stored chunks (drops and recreates the collection)."""
    store = get_vectorstore(settings)
    store.delete_collection()
