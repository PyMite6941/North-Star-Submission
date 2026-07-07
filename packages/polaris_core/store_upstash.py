"""Upstash Vector backend for the app store (managed, serverless, higher-scale writes).

Same interface as the Chroma backend in ``store.py``: put/get/all/search/delete/delete_kind.
Vectors are computed with the same embedder (fastembed/Ollama); Upstash stores them with
arbitrary JSON metadata and does server-side metadata filtering, so nothing loses
functionality. Activate with ``POLARIS_VECTOR_BACKEND=upstash`` + the two URL/token vars.
"""

from __future__ import annotations

import time
import uuid
from functools import lru_cache
from typing import Any

from polaris_core.config import get_settings
from polaris_core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _index():
    from upstash_vector import Index

    s = get_settings()
    if not (s.upstash_vector_url and s.upstash_vector_token):
        raise RuntimeError(
            "Upstash backend selected but UPSTASH_VECTOR_REST_URL / _TOKEN are not set."
        )
    return Index(url=s.upstash_vector_url, token=s.upstash_vector_token)


@lru_cache(maxsize=1)
def _embedder():
    from polaris_core.embeddings import get_embeddings

    return get_embeddings()


def _embed(text: str) -> list[float]:
    return _embedder().embed_query(text or " ")


class Record(dict):
    """Same shape as store.Record: id, kind, text + metadata fields."""


def _to_record(vec) -> Record:
    meta = dict(vec.metadata or {})
    r = Record(meta)
    r["id"] = vec.id
    r["text"] = meta.get("__text", "")
    r.pop("__text", None)
    return r


def put(kind: str, text: str, meta: dict[str, Any] | None = None, id: str | None = None) -> str:
    rid = id or f"{kind}:{uuid.uuid4().hex[:12]}"
    metadata = {**(meta or {}), "kind": kind, "updated_at": time.time(), "__text": text or " "}
    _index().upsert(vectors=[(rid, _embed(text), metadata)])
    return rid


def get(id: str) -> Record | None:
    res = _index().fetch(ids=[id], include_metadata=True, include_vectors=False)
    vec = res[0] if res else None
    return _to_record(vec) if vec else None


def _filter(where: dict[str, Any] | None) -> str | None:
    if not where:
        return None
    parts = []
    for k, v in where.items():
        parts.append(f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}")
    return " AND ".join(parts)


def all(kind: str, where: dict[str, Any] | None = None) -> list[Record]:
    flt = _filter({"kind": kind, **(where or {})})
    out: list[Record] = []
    cursor = ""
    while True:
        res = _index().range(cursor=cursor, limit=200, include_metadata=True, filter=flt or "")
        out.extend(_to_record(v) for v in res.vectors)
        cursor = res.next_cursor
        if not cursor:
            break
    return out


def search(kind: str | None, text: str, k: int = 5) -> list[Record]:
    flt = _filter({"kind": kind}) if kind else None
    res = _index().query(
        vector=_embed(text), top_k=k, include_metadata=True, filter=flt or ""
    )
    return [_to_record(v) for v in res]


def delete(id: str) -> None:
    _index().delete(ids=[id])


def delete_kind(kind: str) -> int:
    items = all(kind)
    if items:
        _index().delete(ids=[r["id"] for r in items])
    return len(items)
