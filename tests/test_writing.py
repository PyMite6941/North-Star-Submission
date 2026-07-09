"""Tests for the offline writing rule engine (no AI, no Ollama)."""

from __future__ import annotations


def test_detects_wordiness_and_suggests_fix():
    from writing.check import check

    report = check("In order to succeed, work hard.")
    wordy = [i for i in report.issues if i.matched.lower() == "in order to"]
    assert wordy and wordy[0].suggestion == "to"
    assert wordy[0].type == "clarity"


def test_flags_weasel_and_repeats_and_confusables():
    from writing.check import check

    issues = check("This is very very good. Its clearly better.").issues
    assert any("Weak intensifier" in i.message for i in issues)          # weasel
    assert any("Repeated word" in i.message for i in issues)             # "very very"
    assert any(i.type == "grammar" and "confused" in i.message for i in issues)  # its/it's


def test_score_rewards_clean_prose():
    from writing.check import check

    clean = check("The cell makes energy. Light drives the reaction.").score
    messy = check(
        "In order to make energy, the the cell is very very clearly used "
        "due to the fact that light."
    ).score
    assert clean > messy
    assert 0 <= messy <= 100


def test_issue_spans_are_valid():
    from writing.check import check

    text = "Due to the fact that it works, we are pleased."
    for i in check(text).issues:
        assert 0 <= i.start <= i.end <= len(text)
        assert text[i.start:i.end]  # non-empty span


def test_writing_router_registered():
    import pytest

    pytest.importorskip("fastapi")
    from polaris_api.app import app

    paths = set(app.openapi()["paths"])
    assert {"/writing/check", "/writing/coach", "/writing/polish"} <= paths
