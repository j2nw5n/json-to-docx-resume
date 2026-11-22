"""Translate parsed resume data into the DOCX template's Jinja context.

This is the boundary between "valid resume data" (owned by
resume_docx.parsers) and "what the template can render" (owned here).
Template-shaped conventions live in this module, not in a parser — a
different template would change these rules without touching how JSON
Resume is validated.
"""

from __future__ import annotations

from typing import Any

from resume_docx.errors import ResumeValidationError

__all__ = ["EARLIER_EXPERIENCE_NAME", "build_context"]

# Convention: a work[] entry with this exact name is the designated
# "Earlier Experience" bucket, not a real job block — it renders under the
# template's Earlier Experience heading with just a summary paragraph (no
# job title, no bullets, no date range).
EARLIER_EXPERIENCE_NAME = "Earlier Experience"


def _date_range(start: str | None, end: str | None) -> str:
    if not start:
        raise ResumeValidationError("work entry is missing required field: startDate")
    start_year = start[:4]
    end_year = end[:4] if end else "Present"
    return f"{start_year}–{end_year}"


def build_context(resume: dict[str, Any]) -> dict[str, Any]:
    """Translate parsed JSON Resume data into the template's Jinja context.
    No job-count limit — docxtpl's {%p for %} handles any number of jobs."""
    basics = resume.get("basics", {})
    work = resume["work"]

    real_jobs = [w for w in work if (w.get("name") or "").strip() != EARLIER_EXPERIENCE_NAME]
    earlier = [w for w in work if (w.get("name") or "").strip() == EARLIER_EXPERIENCE_NAME]
    if len(earlier) > 1:
        raise ResumeValidationError(
            f"Resume has {len(earlier)} work[] entries named '{EARLIER_EXPERIENCE_NAME}', "
            "but only one is supported. Combine them into a single entry."
        )
    for entry in earlier:
        if not entry.get("summary"):
            raise ResumeValidationError(
                f"The '{EARLIER_EXPERIENCE_NAME}' work[] entry is missing required field: summary"
            )

    jobs_context = [
        {
            "name": job.get("name", ""),
            "location": job.get("location", ""),
            "position": job.get("position", ""),
            "date_range": _date_range(job.get("startDate"), job.get("endDate")),
            "summary": job.get("summary", ""),
            "highlights": job.get("highlights") or [],
        }
        for job in real_jobs
    ]

    return {
        "basics": basics,
        "skills": resume.get("skills") or [],
        "work": jobs_context,
        "earlier_experience": earlier[0] if earlier else None,
        "education": resume.get("education") or [],
    }
