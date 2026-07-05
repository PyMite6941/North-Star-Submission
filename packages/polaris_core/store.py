"""Generic Chroma-backed store for the app's own feature data.

Everything (syllabus courses, assignments, clubs, events, decks, cards, pomodoro sessions)
lives as an embedded document in one local Chroma collection, tagged with a ``kind`` plus
arbitrary structured metadata. This gives every feature:
  * semantic search (embedding similarity), and
  * exact filtering/aggregation over metadata (dates, weights, SM-2 state) in Python.

A single collection keeps cross-feature queries trivial (e.g. the planner reading the
syllabus's assignments) and lets the free-API interpreter reason over all of it.
"""

from __future__ import annotations

import json
import time
import uuid
from functools import lru_cache
from typing import Any

from polaris_core.config import get_settings
from polaris_core.logging import get_logger

logger = get_logger(__name__)

# Chroma metadata values must be str/int/float/bool. We JSON-encode anything else and
# transparently decode on the way out, so callers can store lists/dicts freely.
_JSON_PREFIX = "\x00json:"


def _encode(meta: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = _JSON_PREFIX + json.dumps(v)
    return out


def _decode(meta: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in (meta or {}).items():
        if isinstance(v, str) and v.startswith(_JSON_PREFIX):
            try:
                out[k] = json.loads(v[len(_JSON_PREFIX) :])
                continue
            except json.JSONDecodeError:
                pass
        out[k] = v
    return out


@lru_cache(maxsize=1)
def _collection():
    """The embedded Chroma collection (created once per process)."""
    import chromadb

    settings = get_settings()
    client = chromadb.PersistentClient(path=str(settings.chroma_path()))
    return client.get_or_create_collection(settings.app_collection)


@lru_cache(maxsize=1)
def _embedder():
    from polaris_core.embeddings import get_embeddings

    return get_embeddings()


def _embed(text: str) -> list[float]:
    return _embedder().embed_query(text or " ")


class Record(dict):
    """A stored item: has ``id``, ``kind``, ``text`` and decoded metadata fields."""


def put(kind: str, text: str, meta: dict[str, Any] | None = None, id: str | None = None) -> str:
    """Insert or update an item of ``kind``. Returns its id."""
    rid = id or f"{kind}:{uuid.uuid4().hex[:12]}"
    md = _encode({**(meta or {}), "kind": kind, "updated_at": time.time()})
    _collection().upsert(
        ids=[rid], documents=[text or " "], embeddings=[_embed(text)], metadatas=[md]
    )
    return rid


def get(id: str) -> Record | None:
    res = _collection().get(ids=[id], include=["documents", "metadatas"])
    if not res["ids"]:
        return None
    return _to_record(res["ids"][0], res["documents"][0], res["metadatas"][0])


def all(kind: str, where: dict[str, Any] | None = None) -> list[Record]:
    """All items of a kind (optionally filtered by exact metadata)."""
    flt: dict[str, Any] = {"kind": kind}
    if where:
        flt = {"$and": [{"kind": kind}, *[{k: v} for k, v in where.items()]]}
    res = _collection().get(where=flt, include=["documents", "metadatas"])
    return [
        _to_record(i, d, m)
        for i, d, m in zip(res["ids"], res["documents"], res["metadatas"], strict=False)
    ]


def search(kind: str | None, text: str, k: int = 5) -> list[Record]:
    """Semantic search, optionally scoped to a kind."""
    where = {"kind": kind} if kind else None
    res = _collection().query(
        query_embeddings=[_embed(text)],
        n_results=k,
        where=where,
        include=["documents", "metadatas"],
    )
    ids = res["ids"][0] if res["ids"] else []
    docs = res["documents"][0] if res.get("documents") else []
    metas = res["metadatas"][0] if res.get("metadatas") else []
    return [_to_record(i, d, m) for i, d, m in zip(ids, docs, metas, strict=False)]


def delete(id: str) -> None:
    _collection().delete(ids=[id])


def delete_kind(kind: str) -> int:
    items = all(kind)
    if items:
        _collection().delete(ids=[r["id"] for r in items])
    return len(items)


def _to_record(rid: str, doc: str, meta: dict[str, Any]) -> Record:
    r = Record(_decode(meta))
    r["id"] = rid
    r["text"] = doc
    return r
