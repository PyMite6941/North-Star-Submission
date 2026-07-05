"""Typed records for the College Planner."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

#: Allowed application-status values (not enforced strictly — free text also works).
STATUSES = ["researching", "applying", "submitted", "accepted", "rejected", "waitlisted"]


class CollegeEntry(BaseModel):
    """One college on the student's list, with its application status."""

    name: str
    app_type: str = Field(
        default="",
        description="e.g. 'Early Action', 'Early Decision', 'Regular Decision', 'Rolling'.",
    )
    deadline: date | None = Field(default=None, description="Application deadline, if known.")
    status: str = Field(
        default="researching", description="One of college_planner.models.STATUSES."
    )
    notes: str = Field(default="")


class CourseEntry(BaseModel):
    """One course toward the 4-year plan / transcript."""

    subject: str
    course_name: str
    credits: float = Field(default=1.0)
    year: int = Field(description="Grade level the course was/is taken, e.g. 9-12.")
    grade: str = Field(default="", description="Letter grade, or 'in progress'.")
