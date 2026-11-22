"""Generate a styled DOCX resume from a JSON Resume file.

Public API:
    generate(resume_path, template_path, out_path) -> None
    build_context(resume) -> dict
    ResumeValidationError

Importing this package does not pull in tkinter — resume_docx.gui is only
imported when the GUI is actually launched.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from resume_docx.context import EARLIER_EXPERIENCE_NAME, build_context
from resume_docx.errors import ResumeValidationError
from resume_docx.generate import generate

try:
    __version__ = version("json-to-docx-resume")
except PackageNotFoundError:  # not installed (e.g. run straight from a source tree)
    __version__ = "0.0.0+unknown"

__all__ = [
    "EARLIER_EXPERIENCE_NAME",
    "ResumeValidationError",
    "__version__",
    "build_context",
    "generate",
]
