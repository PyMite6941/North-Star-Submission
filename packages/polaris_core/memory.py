"""LangGraph persistence helpers.

A SQLite checkpointer makes graph runs resumable and lets conversations persist
across process restarts, keyed by ``thread_id``.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from polaris_core.config import Settings, get_settings


@contextmanager
def sqlite_checkpointer(settings: Settings | None = None) -> Iterator[object]:
    """Yield a LangGraph ``SqliteSaver`` bound to the configured DB path.

    Usage::

        with sqlite_checkpointer() as cp:
            graph = builder.compile(checkpointer=cp)
            graph.invoke(state, config={"configurable": {"thread_id": "abc"}})
    """
    from langgraph.checkpoint.sqlite import SqliteSaver

    settings = settings or get_settings()
    db_path = str(settings.checkpoint_path())
    with SqliteSaver.from_conn_string(db_path) as saver:
        yield saver
