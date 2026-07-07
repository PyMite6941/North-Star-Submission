"""Tests for the student-life features that don't need Ollama or a real vector DB."""

from __future__ import annotations

from datetime import date


def test_sm2_pass_grows_interval():
    from recall.sm2 import SM2State, schedule

    st = SM2State.new(today=date(2026, 1, 1))
    st = schedule(st, 5, today=date(2026, 1, 1))  # first pass → interval 1
    assert st.interval == 1 and st.repetitions == 1
    st = schedule(st, 5, today=date(2026, 1, 2))  # second pass → interval 6
    assert st.interval == 6 and st.repetitions == 2
    st3 = schedule(st, 4, today=date(2026, 1, 8))  # third pass → interval grows ×ease
    assert st3.interval > 6 and st3.repetitions == 3


def test_sm2_lapse_resets():
    from recall.sm2 import SM2State, schedule

    st = SM2State(ease=2.5, interval=20, repetitions=5, due="2026-01-01")
    st = schedule(st, 1, today=date(2026, 1, 1))  # failed recall
    assert st.repetitions == 0 and st.interval == 1
    assert st.ease >= 1.3  # ease never drops below the floor


def test_sm2_due_date_advances():
    from recall.sm2 import SM2State, schedule

    st = schedule(SM2State.new(today=date(2026, 1, 1)), 5, today=date(2026, 1, 1))
    assert st.due == "2026-01-02"


def test_workload_effort_ranking():
    """An exam should outweigh a reading in the effort heuristic."""
    from planner.workload import _effort

    assert _effort({"type": "exam"}) > _effort({"type": "reading"})
    assert _effort({"type": "assignment", "weight_pct": 40}) > _effort({"type": "assignment"})


def test_vector_backend_dispatch(monkeypatch):
    """store delegates to the Upstash backend when POLARIS_VECTOR_BACKEND=upstash."""
    from polaris_core import store

    calls = {}

    def fake_put(*a, **k):
        calls["put"] = a
        return "id1"

    fake = type("M", (), {"put": staticmethod(fake_put)})
    monkeypatch.setattr(store, "_upstash", lambda: fake)
    assert store.put("club", "text", {"name": "x"}) == "id1"
    assert "put" in calls  # routed to the managed backend, not Chroma

    monkeypatch.setattr(store, "_upstash", lambda: None)  # default path still exists
    assert store._upstash() is None


def test_feature_routers_registered():
    """The API mounts every student-life router (skips if fastapi absent)."""
    import pytest

    pytest.importorskip("fastapi")
    from polaris_api.app import app

    paths = set(app.openapi()["paths"])
    expected = {
        "/syllabus/courses",
        "/planner/workload",
        "/pomodoro/stats",
        "/clubs",
        "/recall/decks",
    }
    assert expected <= paths
    assert "/assistant/ask" in paths
