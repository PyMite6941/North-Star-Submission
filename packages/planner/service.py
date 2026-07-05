"""Smart weekly study plan built from upcoming assignments + workload."""

from __future__ import annotations

from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

from planner.workload import detect_workload

logger = get_logger(__name__)


class StudyBlock(BaseModel):
    day: str = Field(description="Day of week, e.g. 'Monday'.")
    task: str = Field(description="What to work on (tie to a specific assignment/exam).")
    minutes: int = Field(default=60, description="Suggested focus minutes (pomodoro-friendly).")


class WeeklyStudyPlan(BaseModel):
    focus: str = Field(description="The week's top priority.")
    blocks: list[StudyBlock] = Field(description="Study sessions across the week.")


_SYSTEM = (
    "You are a study planner. Given upcoming assignments/exams and detected weekly workload, "
    "produce a realistic one-week study schedule as structured blocks. Front-load work before "
    "heavy weeks and deadlines, keep sessions pomodoro-sized (25–90 min), and include breaks/"
    "lighter days. Tie each block to a specific item."
)


def make_weekly_plan(study_hours_per_day: float = 2.0) -> WeeklyStudyPlan:
    """Generate a weekly plan grounded in the student's detected workload."""
    weeks = detect_workload()
    today = date.today().isoformat()
    upcoming = [w for w in weeks if w.week_start >= today[:10]][:3]
    ctx_lines = [f"Budget: ~{study_hours_per_day} h/day.", f"Today: {today}."]
    if upcoming:
        for w in upcoming:
            tag = " [HEAVY]" if w.heavy else ""
            titles = ", ".join(i.get("title", "?") for i in w.items[:8])
            ctx_lines.append(f"Week of {w.week_start}{tag} (score {w.score:.1f}): {titles}")
    else:
        ctx_lines.append("No dated assignments found — plan general review/study habits.")

    llm = get_chat_model(temperature=0.3, allow_cloud=True)
    plan = llm.with_structured_output(WeeklyStudyPlan).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content="\n".join(ctx_lines))]
    )
    logger.info("Built weekly plan with %d blocks", len(plan.blocks))
    return plan
