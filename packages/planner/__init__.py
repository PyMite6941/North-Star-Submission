"""planner — workload detection and smart weekly planning over the student's data.

Reads assignments (imported by the ``syllabus`` package) from the shared vector store,
buckets them by ISO week to detect workload/heavy weeks, and builds a study plan with the
LLM. Complements the offline ``college_planner`` (deadlines DB) rather than duplicating it.
"""

from planner.service import make_weekly_plan
from planner.workload import WeekLoad, detect_workload

__all__ = ["WeekLoad", "detect_workload", "make_weekly_plan"]
