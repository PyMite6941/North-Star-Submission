"""Typed schema for extracted syllabus data."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Assignment(BaseModel):
    title: str = Field(description="Assignment/exam/project name.")
    type: str = Field(
        default="assignment", description="assignment | exam | quiz | project | reading"
    )
    due_date: str | None = Field(default=None, description="ISO date YYYY-MM-DD if known")
    weight_pct: float | None = Field(default=None, description="Grade weight percent, if stated.")


class Course(BaseModel):
    name: str = Field(description="Course title, e.g. 'AP Biology'.")
    code: str | None = Field(default=None, description="Course code if present.")
    instructor: str | None = None
    term: str | None = None


class ExtractedSyllabus(BaseModel):
    course: Course
    assignments: list[Assignment] = Field(default_factory=list)
