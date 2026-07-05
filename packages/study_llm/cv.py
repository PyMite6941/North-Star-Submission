"""Structured CV/résumé generation + export.

Mirrors ``flashcards.py``: uses the LLM's structured-output mode to produce a typed,
sectioned résumé (not free text), so it renders consistently and exports cleanly to
Markdown (to edit further) or PDF (to upload to a college/job portal or print) — no
North Star install needed on the receiving end either way.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class ContactInfo(BaseModel):
    """Header contact details."""

    name: str = Field(description="Full name.")
    email: str = Field(default="", description="Email address, or '' if unknown.")
    phone: str = Field(default="", description="Phone number, or '' if unknown.")
    location: str = Field(default="", description="City/region, or '' if unknown.")
    links: list[str] = Field(
        default_factory=list, description="Portfolio/LinkedIn/GitHub URLs, if any."
    )


class ExperienceEntry(BaseModel):
    title: str = Field(description="Role/title.")
    organization: str = Field(description="Employer, club, or organization.")
    dates: str = Field(default="", description="e.g. 'Jun 2024 - Aug 2024'.")
    bullets: list[str] = Field(
        description="Action-verb, quantified impact bullets (2-4 per entry)."
    )


class EducationEntry(BaseModel):
    school: str = Field(description="School name.")
    credential: str = Field(default="", description="e.g. 'High School Diploma', 'GPA 3.9'.")
    dates: str = Field(default="", description="e.g. 'Class of 2027'.")
    details: list[str] = Field(
        default_factory=list, description="Honors, relevant coursework, activities."
    )


class ProjectEntry(BaseModel):
    name: str = Field(description="Project name.")
    bullets: list[str] = Field(description="What it is / what you did / the outcome.")


class Resume(BaseModel):
    """A structured, ATS-friendly résumé."""

    contact: ContactInfo
    summary: str = Field(default="", description="1-2 sentence professional summary.")
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)


_SYSTEM = (
    "You are a professional CV/résumé writer, specializing in résumés for high-school "
    "students applying to college, internships, or a first job. Produce strong, "
    "ATS-friendly content with action verbs and quantified impact where possible. Use "
    "sensible placeholders for anything not provided (e.g. '[Add GPA]') rather than "
    "inventing facts. Sections: contact, summary, experience, education, skills, projects."
)


def generate_resume(details: str) -> Resume:
    """Generate a structured :class:`Resume` from free-form `details` about the student."""
    llm = get_chat_model(temperature=0.3)
    resume = llm.with_structured_output(Resume).invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=details)]
    )
    logger.info("Generated resume for %r", resume.contact.name or "(unnamed)")
    return resume


def to_markdown(resume: Resume) -> str:
    """Render a :class:`Resume` as clean Markdown."""
    lines: list[str] = [f"# {resume.contact.name}"]

    contact = resume.contact
    contact_bits = [b for b in (contact.email, contact.phone, contact.location) if b]
    contact_bits.extend(contact.links)
    if contact_bits:
        lines.append(" | ".join(contact_bits))

    if resume.summary:
        lines += ["", "## Summary", resume.summary]

    if resume.experience:
        lines += ["", "## Experience"]
        for e in resume.experience:
            header = f"**{e.title}**, {e.organization}"
            if e.dates:
                header += f" ({e.dates})"
            lines.append(header)
            lines += [f"- {b}" for b in e.bullets]

    if resume.education:
        lines += ["", "## Education"]
        for ed in resume.education:
            header = f"**{ed.school}**"
            if ed.credential:
                header += f" — {ed.credential}"
            if ed.dates:
                header += f" ({ed.dates})"
            lines.append(header)
            lines += [f"- {d}" for d in ed.details]

    if resume.skills:
        lines += ["", "## Skills", ", ".join(resume.skills)]

    if resume.projects:
        lines += ["", "## Projects"]
        for p in resume.projects:
            lines.append(f"**{p.name}**")
            lines += [f"- {b}" for b in p.bullets]

    return "\n".join(lines) + "\n"


def export_markdown(resume: Resume, path: str | Path) -> Path:
    """Write the résumé as a Markdown file. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(resume), encoding="utf-8")
    logger.info("Exported resume → %s", path)
    return path


def _pdf_section(pdf, title: str) -> None:
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)


def to_pdf_bytes(resume: Resume) -> bytes:
    """Render a :class:`Resume` as a one-page-style PDF (bytes) — no extra fonts needed."""
    from fpdf import FPDF

    pdf = FPDF(format="Letter")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, resume.contact.name or "Résumé", new_x="LMARGIN", new_y="NEXT")

    contact = resume.contact
    contact_bits = [b for b in (contact.email, contact.phone, contact.location) if b]
    contact_bits.extend(contact.links)
    if contact_bits:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, " | ".join(contact_bits), new_x="LMARGIN", new_y="NEXT")

    if resume.summary:
        _pdf_section(pdf, "Summary")
        pdf.multi_cell(0, 6, resume.summary)

    if resume.experience:
        _pdf_section(pdf, "Experience")
        for e in resume.experience:
            header = f"{e.title}, {e.organization}"
            if e.dates:
                header += f" ({e.dates})"
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, header)
            pdf.set_font("Helvetica", "", 11)
            for b in e.bullets:
                pdf.multi_cell(0, 6, f"- {b}")

    if resume.education:
        _pdf_section(pdf, "Education")
        for ed in resume.education:
            header = ed.school
            if ed.credential:
                header += f" - {ed.credential}"
            if ed.dates:
                header += f" ({ed.dates})"
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, header)
            pdf.set_font("Helvetica", "", 11)
            for d in ed.details:
                pdf.multi_cell(0, 6, f"- {d}")

    if resume.skills:
        _pdf_section(pdf, "Skills")
        pdf.multi_cell(0, 6, ", ".join(resume.skills))

    if resume.projects:
        _pdf_section(pdf, "Projects")
        for p in resume.projects:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, p.name)
            pdf.set_font("Helvetica", "", 11)
            for b in p.bullets:
                pdf.multi_cell(0, 6, f"- {b}")

    return bytes(pdf.output())


def export_pdf(resume: Resume, path: str | Path) -> Path:
    """Write the résumé as a PDF file. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_pdf_bytes(resume))
    logger.info("Exported resume → %s (.pdf)", path)
    return path


def export_resume(resume: Resume, path: str | Path) -> Path:
    """Export the résumé, choosing the format from `path`'s suffix (`.pdf` or Markdown)."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return export_pdf(resume, path)
    return export_markdown(resume, path)
