"""Ingestion: load notes → split into chunks → embed → store in Chroma.

Supports Markdown/txt/rst plus PDF, DOCX, and PPTX. Ingestion is **incremental**:
each file's content is hashed, so re-ingesting skips unchanged files and re-indexes
(upserts) changed ones instead of piling up duplicate chunks.

Run whenever notes change. Retrieval afterwards is fully offline.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from polaris_core.config import Settings, get_settings
from polaris_core.documents import SUPPORTED, iter_files, read_file
from polaris_core.logging import get_logger

from study_rag.store import get_vectorstore

logger = get_logger(__name__)

# Supported note formats (.md/.txt/.rst/.pdf/.docx/.pptx) — see polaris_core.documents.
__all__ = ["ingest_path", "SUPPORTED"]


def _content_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def ingest_path(target: str | Path, settings: Settings | None = None) -> int:
    """Ingest a file or directory of notes (incrementally). Returns chunks added/updated.

    Unchanged files (matching stored content hash) are skipped; changed files have their
    old chunks removed and replaced.
    """
    settings = settings or get_settings()
    path = Path(target)
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")

    store = get_vectorstore(settings)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        add_start_index=True,
    )

    total_new = 0
    skipped = 0
    for f in iter_files(path):
        text = read_file(f)
        if not text or not text.strip():
            continue
        source = str(f)
        digest = _content_hash(text)

        # Dedupe: compare against any existing chunks for this source.
        existing = store.get(where={"source": source}, include=["metadatas"])
        existing_ids = existing.get("ids", [])
        existing_hashes = {m.get("content_hash") for m in existing.get("metadatas", [])}
        if existing_ids and existing_hashes == {digest}:
            skipped += 1
            continue
        if existing_ids:
            store.delete(ids=existing_ids)  # file changed → drop stale chunks

        doc = Document(
            page_content=text,
            metadata={"source": source, "title": f.stem, "content_hash": digest},
        )
        chunks = splitter.split_documents([doc])
        store.add_documents(chunks)
        total_new += len(chunks)
        logger.info("Indexed %s → %d chunks", f.name, len(chunks))

    if skipped:
        logger.info("Skipped %d unchanged file(s).", skipped)
    if total_new == 0 and skipped == 0:
        logger.warning("No supported files found under %s", path)
    logger.info("Stored %d new/updated chunks in %r", total_new, settings.rag_collection)
    return total_new
