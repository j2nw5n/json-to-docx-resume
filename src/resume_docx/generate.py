"""Render a styled DOCX resume from a JSON Resume file.

Parses the resume (resume_docx.parsers), builds the template context
(resume_docx.context), and renders a Jinja-tagged docxtpl template. The
template file itself is never modified — only out_path is written.
"""

from __future__ import annotations

from pathlib import Path

from docxtpl import DocxTemplate

from resume_docx.context import EARLIER_EXPERIENCE_NAME, build_context
from resume_docx.errors import ResumeValidationError
from resume_docx.parsers import json_resume

__all__ = [
    "EARLIER_EXPERIENCE_NAME",
    "ResumeValidationError",
    "build_context",
    "generate",
]


def generate(resume_path: str | Path, template_path: str | Path, out_path: str | Path) -> None:
    resume = json_resume.parse(resume_path)
    context = build_context(resume)

    tpl = DocxTemplate(str(template_path))
    # autoescape is required, not cosmetic: a DOCX body is XML, so resume data
    # containing &, < or > is otherwise injected raw. Without it, "R&D" renders
    # as "RD" and a single "<" swallows the rest of the document — silently, with
    # a valid-looking file on disk. docxtpl defaults this to False.
    tpl.render(context, autoescape=True)
    tpl.save(str(out_path))
