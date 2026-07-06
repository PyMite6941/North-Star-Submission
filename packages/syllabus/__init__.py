"""syllabus — import a syllabus file, extract structured course + assignments, store them.

Uses the LLM's structured-output mode to parse a messy syllabus into courses, assignments,
and exams, then persists each as an embedded item in the shared vector store so the planner
and the interpreter can reason over deadlines and workload.
"""

from syllabus.models import Assignment, Course, ExtractedSyllabus
from syllabus.service import (
    import_syllabus_file,
    import_syllabus_text,
    list_assignments,
    list_courses,
)

__all__ = [
    "Assignment",
    "Course",
    "ExtractedSyllabus",
    "import_syllabus_file",
    "import_syllabus_text",
    "list_assignments",
    "list_courses",
]
