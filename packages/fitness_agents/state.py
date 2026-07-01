"""Graph state for the fitness agent pipeline."""

from __future__ import annotations

from typing import TypedDict


class FitnessState(TypedDict, total=False):
    """State threaded through the fitness pipeline.

    - ``files``: input file paths to parse.
    - ``goal``: optional user goal (e.g. "run a sub-25 5K").
    - ``metrics_text``: human-readable metrics summary across all files.
    - ``n_records``: total parsed samples.
    - ``sessions``: per-file {source, date, summary} for optional history logging.
    - ``trend_text``: progress trends (fitness/fatigue/form) from stored history, if any.
    - ``analysis``: analyst agent output.
    - ``plan``: growth-plan agent output.
    - ``review``: reviewer agent's critique / final polish.
    """

    files: list[str]
    goal: str
    metrics_text: str
    n_records: int
    sessions: list
    trend_text: str
    analysis: str
    plan: str
    review: str
