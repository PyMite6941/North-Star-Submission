"""Embeddings factory — Ollama by default, fastembed (ONNX) as an offline fallback."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from polaris_core.config import Settings, get_settings
from polaris_core.logging import get_logger

logger = get_logger(__name__)


def get_embeddings(settings: Settings | None = None) -> Embeddings:
    """Return an embeddings model per ``POLARIS_EMBED_BACKEND``.

    - ``ollama`` (default): uses the configured embed model via the local daemon.
    - ``fastembed``: pure-offline ONNX embeddings (needs the ``offline-embeddings`` extra).
    """
    settings = settings or get_settings()

    if settings.embed_backend == "fastembed":
        try:
            from langchain_community.embeddings import FastEmbedEmbeddings
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "fastembed backend requires the extra: "
                'pip install -e ".[offline-embeddings]"'
            ) from exc
        logger.info("Using FastEmbed embeddings: %s", settings.fastembed_model)
        return FastEmbedEmbeddings(model_name=settings.fastembed_model)

    from langchain_ollama import OllamaEmbeddings

    logger.info("Using Ollama embeddings: %s", settings.embed_model)
    return OllamaEmbeddings(model=settings.embed_model, base_url=settings.ollama_base_url)
