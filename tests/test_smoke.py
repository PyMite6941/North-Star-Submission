"""Smoke tests that do NOT require a running Ollama daemon.

They verify the scaffolding wires together: config loads, the 6 areas exist,
parsers + metrics work, and the markdown agents are discoverable.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_settings_load():
    from polaris_core.config import get_settings

    s = get_settings()
    assert s.chat_model
    assert s.rag_top_k >= 1


def test_six_polaris_areas():
    from polaris_core.polaris import POLARIS_AREAS, PolarisArea

    assert len(PolarisArea) == 6
    assert len(POLARIS_AREAS) == 6
    # every area has a non-empty specialized system prompt
    assert all(info.system_prompt for info in POLARIS_AREAS.values())


def test_csv_parser_and_metrics():
    from fitness_agents.metrics import summarize
    from fitness_agents.parsers import parse_file

    sample = REPO / "fitness agents for use" / "sample_data" / "run.csv"
    records = parse_file(sample)
    assert len(records) == 10
    summary = summarize(records)
    assert summary.n_samples == 10
    assert summary.distance_km and summary.distance_km > 1.5
    assert summary.avg_heart_rate and 120 < summary.avg_heart_rate < 175


def test_hr_zones_and_training_load():
    """New metrics: HR zones sum to ~1.0 and training load is positive."""
    from fitness_agents.metrics import summarize
    from fitness_agents.parsers import parse_file

    sample = REPO / "fitness agents for use" / "sample_data" / "run.csv"
    summary = summarize(parse_file(sample))
    assert summary.training_load and summary.training_load > 0
    assert summary.hr_zones is not None
    assert abs(sum(summary.hr_zones.values()) - 1.0) < 1e-6


def test_flashcard_export(tmp_path):
    """Deck export writes an Anki-importable CSV (no LLM needed)."""
    import csv

    from study_llm.flashcards import Deck, Flashcard, export_csv

    deck = Deck(topic="Test", cards=[Flashcard(question="Q1", answer="A1")])
    out = export_csv(deck, tmp_path / "deck.csv")
    rows = list(csv.reader(open(out, encoding="utf-8")))
    assert rows == [["Q1", "A1"]]


def test_fitness_agents_present():
    from fitness_agents.agents import list_agents

    names = set(list_agents())
    assert {"fitness_analyst", "growth_planner", "plan_reviewer"} <= names


def test_graphs_build():
    """Graphs compile without contacting any model (nodes are lazy)."""
    import fitness_agents.graph as fg
    import study_llm.graph as sg
    import study_rag.graph as rg

    assert sg.build_graph() is not None
    assert rg.build_graph() is not None
    assert fg.build_graph() is not None


def test_unified_cli_mounts_subcommands():
    """The umbrella `polaris` CLI mounts study/rag/fitness groups."""
    from polaris_cli.main import app

    groups = {g.name for g in app.registered_groups}
    assert {"study", "rag", "fitness"} <= groups


def test_hr_zones_use_profile_max_hr():
    """Passing an explicit max HR changes the zone reference."""
    from fitness_agents.metrics import summarize
    from fitness_agents.parsers import parse_file

    sample = REPO / "fitness agents for use" / "sample_data" / "run.csv"
    records = parse_file(sample)
    # With a higher max HR the same efforts land in lower zones (less time in Z5).
    low_ref = summarize(records, max_hr=170).hr_zones
    high_ref = summarize(records, max_hr=210).hr_zones
    assert low_ref["Z5"] >= high_ref["Z5"]


def test_ics_export(tmp_path):
    """Schedule exports a valid iCalendar file (no LLM needed)."""
    from fitness_agents.schedule import WeeklySchedule, Workout, export_ics

    workout = Workout(day="Monday", title="Easy run", description="30 min Z2", duration_min=30)
    sched = WeeklySchedule(goal="test", workouts=[workout])
    out = export_ics(sched, tmp_path / "plan.ics")
    text = out.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in text
    assert "BEGIN:VEVENT" in text
    assert "Easy run" in text


def test_history_log_and_trends(tmp_path):
    """Logging a session then computing trends works against a temp DB."""
    import os

    from polaris_core.config import get_settings

    old = os.environ.get("POLARIS_FITNESS_DB")
    os.environ["POLARIS_FITNESS_DB"] = str(tmp_path / "fit.sqlite")
    get_settings.cache_clear()
    try:
        from fitness_agents import history
        from fitness_agents.metrics import summarize
        from fitness_agents.parsers import parse_file

        summary = summarize(parse_file(REPO / "fitness agents for use" / "sample_data" / "run.csv"))
        history.log_session(summary, "run.csv")
        trends = history.compute_trends()
        assert trends is not None and trends.n_sessions == 1
        assert trends.total_distance_km > 1.5
    finally:
        if old is None:
            os.environ.pop("POLARIS_FITNESS_DB", None)
        else:
            os.environ["POLARIS_FITNESS_DB"] = old
        get_settings.cache_clear()


def test_api_app_has_routes():
    """FastAPI app exposes the expected endpoints (skips if serve extra absent)."""
    import pytest

    pytest.importorskip("fastapi")
    from polaris_api.app import app

    paths = {r.path for r in app.routes}
    assert {"/health", "/study/ask", "/rag/ask", "/fitness/analyze"} <= paths
