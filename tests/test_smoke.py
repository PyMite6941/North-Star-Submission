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


def test_flashcard_apkg_export(tmp_path):
    """Deck export writes a double-click-importable Anki .apkg (no LLM needed)."""
    import sqlite3
    import zipfile

    from study_llm.flashcards import Deck, Flashcard, export_apkg, export_deck

    deck = Deck(topic="Cell Biology", cards=[Flashcard(question="Q1", answer="A1")])
    out = export_apkg(deck, tmp_path / "deck.apkg")
    assert out.exists()
    assert zipfile.is_zipfile(out)

    # export_deck should dispatch on the file suffix.
    out2 = export_deck(deck, tmp_path / "deck2.apkg")
    with zipfile.ZipFile(out2) as zf:
        zf.extract("collection.anki2", tmp_path)
    conn = sqlite3.connect(tmp_path / "collection.anki2")
    (note_count,) = conn.execute("SELECT COUNT(*) FROM notes").fetchone()
    assert note_count == 1
    conn.close()


def test_resume_markdown_export(tmp_path):
    """Résumé export writes clean Markdown (no LLM needed)."""
    from study_llm.cv import ContactInfo, EducationEntry, Resume, export_markdown

    resume = Resume(
        contact=ContactInfo(name="Jordan Lee", email="jordan@example.com"),
        summary="Motivated high-school senior interested in CS.",
        education=[EducationEntry(school="Lincoln High School", credential="GPA 3.9")],
        skills=["Python", "Public speaking"],
    )
    out = export_markdown(resume, tmp_path / "resume.md")
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Jordan Lee")
    assert "jordan@example.com" in text
    assert "## Education" in text
    assert "Lincoln High School" in text
    assert "Python, Public speaking" in text


def test_resume_pdf_export(tmp_path):
    """Résumé export writes a real PDF (no LLM needed)."""
    from study_llm.cv import ContactInfo, EducationEntry, Resume, export_pdf, export_resume

    resume = Resume(
        contact=ContactInfo(name="Jordan Lee", email="jordan@example.com"),
        summary="Motivated high-school senior interested in CS.",
        education=[EducationEntry(school="Lincoln High School", credential="GPA 3.9")],
        skills=["Python", "Public speaking"],
    )
    out = export_pdf(resume, tmp_path / "resume.pdf")
    assert out.read_bytes().startswith(b"%PDF-")

    # export_resume should dispatch on the file suffix.
    out2 = export_resume(resume, tmp_path / "resume2.pdf")
    assert out2.read_bytes().startswith(b"%PDF-")
    out3 = export_resume(resume, tmp_path / "resume3.md")
    assert out3.read_text(encoding="utf-8").startswith("# Jordan Lee")


def test_quiz_markdown_export(tmp_path):
    """Quiz export writes a printable handout with questions before the answer key."""
    from study_llm.quiz import Quiz, QuizQuestion, export_markdown

    quiz = Quiz(
        topic="Photosynthesis",
        questions=[
            QuizQuestion(
                question="What pigment absorbs light?",
                options=["Chlorophyll", "Melanin"],
                answer="Chlorophyll",
                explanation="Chlorophyll absorbs red/blue light for photosynthesis.",
            )
        ],
    )
    out = export_markdown(quiz, tmp_path / "handout.md")
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Quiz — Photosynthesis")
    assert text.index("What pigment absorbs light?") < text.index("## Answer key")
    assert "Chlorophyll absorbs red/blue light" in text


def test_study_pack_export_import_roundtrip(tmp_path):
    """A Study Pack round-trips through its portable JSON file (no LLM needed)."""
    from study_llm.flashcards import Deck, Flashcard
    from study_llm.groups import StudyPack, export_pack, import_pack
    from study_llm.quiz import Quiz, QuizQuestion

    pack = StudyPack(
        name="Bio final",
        notes="Split the two decks between us.",
        decks=[
            Deck(topic="Krebs cycle", cards=[Flashcard(question="Q1", answer="A1")]),
            Deck(topic="Photosynthesis", cards=[Flashcard(question="Q2", answer="A2")]),
        ],
        quizzes=[
            Quiz(
                topic="Krebs cycle",
                questions=[
                    QuizQuestion(
                        question="Where?", options=[], answer="Mitochondria", explanation="x"
                    )
                ],
            )
        ],
    )
    out = export_pack(pack, tmp_path / "pack.json")
    loaded = import_pack(out)
    assert loaded.name == "Bio final"
    assert [d.topic for d in loaded.decks] == ["Krebs cycle", "Photosynthesis"]
    assert loaded.quizzes[0].questions[0].answer == "Mitochondria"


def test_group_quiz_leaderboard_ranks_and_breaks_ties():
    """Leaderboard sorts by score desc, ties broken alphabetically (no LLM needed)."""
    from study_llm.groups import PlayerResult, leaderboard

    results = [
        PlayerResult(name="Sam", score=3, total=5),
        PlayerResult(name="Ana", score=4, total=5),
        PlayerResult(name="Zoe", score=4, total=5),
    ]
    ranked = leaderboard(results)
    assert [r.name for r in ranked] == ["Ana", "Zoe", "Sam"]


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
    """The umbrella `polaris` CLI mounts study/rag/fitness/college groups."""
    from polaris_cli.main import app

    groups = {g.name for g in app.registered_groups}
    assert {"study", "rag", "fitness", "college"} <= groups


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


def test_college_planner_storage_and_ics_export(tmp_path):
    """Colleges/courses persist to a temp SQLite DB, and deadlines export to .ics."""
    import os

    from polaris_core.config import get_settings

    old = os.environ.get("POLARIS_COLLEGE_DB")
    os.environ["POLARIS_COLLEGE_DB"] = str(tmp_path / "college.sqlite")
    get_settings.cache_clear()
    try:
        from datetime import date

        from college_planner import storage
        from college_planner.calendar_export import export_deadlines_ics
        from college_planner.models import CollegeEntry, CourseEntry

        storage.add_college(
            CollegeEntry(name="MIT", app_type="Early Action", deadline=date(2027, 1, 1))
        )
        storage.add_college(CollegeEntry(name="State U"))
        storage.update_status("MIT", "submitted")
        colleges = storage.list_colleges()
        assert {c.name for c in colleges} == {"MIT", "State U"}
        assert next(c for c in colleges if c.name == "MIT").status == "submitted"

        storage.add_course(
            CourseEntry(subject="Math", course_name="AP Calculus BC", credits=1.0, year=12)
        )
        assert storage.total_credits() == 1.0

        dated = [c for c in colleges if c.deadline is not None]
        out = export_deadlines_ics(dated, tmp_path / "deadlines.ics")
        text = out.read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in text
        assert "MIT application deadline (Early Action)" in text

        assert storage.remove_college("State U") is True
        assert {c.name for c in storage.list_colleges()} == {"MIT"}
    finally:
        if old is None:
            os.environ.pop("POLARIS_COLLEGE_DB", None)
        else:
            os.environ["POLARIS_COLLEGE_DB"] = old
        get_settings.cache_clear()


def test_invalid_embed_backend_fails_fast():
    """A typo'd POLARIS_EMBED_BACKEND should raise, not silently fall back to Ollama."""
    import os

    import pytest
    from polaris_core.config import get_settings
    from pydantic import ValidationError

    old = os.environ.get("POLARIS_EMBED_BACKEND")
    os.environ["POLARIS_EMBED_BACKEND"] = "bogus"
    get_settings.cache_clear()
    try:
        with pytest.raises(ValidationError):
            get_settings()
    finally:
        if old is None:
            os.environ.pop("POLARIS_EMBED_BACKEND", None)
        else:
            os.environ["POLARIS_EMBED_BACKEND"] = old
        get_settings.cache_clear()


def test_fitness_units_toggle_imperial():
    """POLARIS_UNITS=imperial renders miles/mph instead of km/km-h."""
    import os

    from fitness_agents.metrics import summarize
    from fitness_agents.parsers import parse_file
    from polaris_core.config import get_settings

    records = parse_file(REPO / "fitness agents for use" / "sample_data" / "run.csv")
    summary = summarize(records)

    assert "km" in summary.to_prompt(units="metric")
    assert "mi" in summary.to_prompt(units="imperial")

    old = os.environ.get("POLARIS_UNITS")
    os.environ["POLARIS_UNITS"] = "imperial"
    get_settings.cache_clear()
    try:
        assert get_settings().units == "imperial"
        assert "mi" in summary.to_prompt()
    finally:
        if old is None:
            os.environ.pop("POLARIS_UNITS", None)
        else:
            os.environ["POLARIS_UNITS"] = old
        get_settings.cache_clear()


def test_config_show_command():
    """`polaris config show` prints resolved settings and masks secrets."""
    from polaris_cli.main import app
    from typer.testing import CliRunner

    result = CliRunner().invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "POLARIS_CHAT_MODEL" in result.output
    assert "GROQ_API_KEY" in result.output
    assert "not set" in result.output or "***set***" in result.output


def test_cloud_fallback_requires_explicit_admin_opt_in():
    """A configured key alone must not enable cloud use: the admin switch also has to be on."""
    import os

    from polaris_core.config import get_settings

    settings = get_settings()
    assert settings.allow_cloud_fallback is False
    assert settings.cloud_fallback_active is False

    old = os.environ.get("GROQ_API_KEY")
    os.environ["GROQ_API_KEY"] = "fake-key-for-test"
    get_settings.cache_clear()
    try:
        s = get_settings()
        assert s.has_cloud_fallback is True
        assert s.allow_cloud_fallback is False
        assert s.cloud_fallback_active is False  # key alone is not enough
    finally:
        if old is None:
            os.environ.pop("GROQ_API_KEY", None)
        else:
            os.environ["GROQ_API_KEY"] = old
        get_settings.cache_clear()


def test_allow_cloud_fallback_activates_when_both_set():
    """cloud_fallback_active flips on only once both the key and the admin switch are set."""
    import os

    from polaris_core.config import get_settings

    old_key = os.environ.get("GROQ_API_KEY")
    old_switch = os.environ.get("POLARIS_ALLOW_CLOUD_FALLBACK")
    os.environ["GROQ_API_KEY"] = "fake-key-for-test"
    os.environ["POLARIS_ALLOW_CLOUD_FALLBACK"] = "true"
    get_settings.cache_clear()
    try:
        assert get_settings().cloud_fallback_active is True
    finally:
        for name, old in (("GROQ_API_KEY", old_key), ("POLARIS_ALLOW_CLOUD_FALLBACK", old_switch)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        get_settings.cache_clear()


def test_api_app_has_routes():
    """FastAPI app exposes the expected endpoints (skips if serve extra absent)."""
    import pytest

    pytest.importorskip("fastapi")
    from polaris_api.app import app

    paths = {r.path for r in app.routes}
    assert {"/health", "/study/ask", "/study/cv", "/rag/ask", "/fitness/analyze"} <= paths
