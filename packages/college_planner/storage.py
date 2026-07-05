"""Local SQLite storage for the College Planner — no account, no cloud, no sync.

Mirrors `fitness_agents/history.py`'s pattern: a small local DB is what turns this from
a single in-memory session into something a student actually tracks over time.
"""

from __future__ import annotations

import sqlite3
from datetime import date

from polaris_core.config import get_settings
from polaris_core.logging import get_logger

from college_planner.models import CollegeEntry, CourseEntry

logger = get_logger(__name__)


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(str(get_settings().college_path()))
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            app_type TEXT,
            deadline TEXT,
            status TEXT,
            notes TEXT
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            course_name TEXT NOT NULL,
            credits REAL,
            year INTEGER,
            grade TEXT
        )
        """
    )
    return con


def add_college(entry: CollegeEntry) -> int:
    """Insert (or update, if the name already exists) a college. Returns the row id."""
    con = _conn()
    cur = con.execute(
        """
        INSERT INTO colleges(name, app_type, deadline, status, notes) VALUES (?,?,?,?,?)
        ON CONFLICT(name) DO UPDATE SET
            app_type=excluded.app_type, deadline=excluded.deadline,
            status=excluded.status, notes=excluded.notes
        """,
        (
            entry.name,
            entry.app_type,
            entry.deadline.isoformat() if entry.deadline else None,
            entry.status,
            entry.notes,
        ),
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    logger.info("Saved college %r", entry.name)
    return row_id


def _row_to_college(row: sqlite3.Row) -> CollegeEntry:
    return CollegeEntry(
        name=row["name"],
        app_type=row["app_type"] or "",
        deadline=date.fromisoformat(row["deadline"]) if row["deadline"] else None,
        status=row["status"] or "researching",
        notes=row["notes"] or "",
    )


def list_colleges() -> list[CollegeEntry]:
    """Return every college, soonest deadline first (no-deadline entries last)."""
    con = _conn()
    rows = con.execute(
        "SELECT * FROM colleges ORDER BY deadline IS NULL, deadline ASC, name ASC"
    ).fetchall()
    con.close()
    return [_row_to_college(r) for r in rows]


def update_status(name: str, status: str) -> bool:
    """Update a college's application status. Returns True if a row was changed."""
    con = _conn()
    cur = con.execute("UPDATE colleges SET status=? WHERE name=?", (status, name))
    con.commit()
    changed = cur.rowcount > 0
    con.close()
    return changed


def remove_college(name: str) -> bool:
    """Remove a college by name. Returns True if a row was deleted."""
    con = _conn()
    cur = con.execute("DELETE FROM colleges WHERE name=?", (name,))
    con.commit()
    changed = cur.rowcount > 0
    con.close()
    return changed


def add_course(entry: CourseEntry) -> int:
    """Insert a course. Returns the new row id."""
    con = _conn()
    cur = con.execute(
        "INSERT INTO courses(subject, course_name, credits, year, grade) VALUES (?,?,?,?,?)",
        (entry.subject, entry.course_name, entry.credits, entry.year, entry.grade),
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    logger.info("Added course %r (year %d)", entry.course_name, entry.year)
    return row_id


def list_courses() -> list[CourseEntry]:
    """Return every course, ordered by year then subject."""
    con = _conn()
    rows = con.execute("SELECT * FROM courses ORDER BY year ASC, subject ASC").fetchall()
    con.close()
    return [
        CourseEntry(
            subject=r["subject"],
            course_name=r["course_name"],
            credits=r["credits"],
            year=r["year"],
            grade=r["grade"] or "",
        )
        for r in rows
    ]


def total_credits() -> float:
    """Sum of credits across every stored course."""
    return sum(c.credits for c in list_courses())


def clear_all() -> None:
    """Delete every college and course. Mainly for tests / a full reset."""
    con = _conn()
    con.execute("DELETE FROM colleges")
    con.execute("DELETE FROM courses")
    con.commit()
    con.close()
