"""JSON Resume (https://jsonresume.org/) format parser.

Owns validation of the JSON Resume format itself — file reading, JSON
decoding, and the format's own required fields (basics.name, a non-empty
work[]). Deliberately knows nothing about what any particular DOCX
template can render — see resume_docx.generate for constraints specific
to the bundled template (job-count limits, the "Earlier Experience"
convention).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from resume_docx.errors import ResumeValidationError


def parse(path: str | Path) -> dict[str, Any]:
    """Load and validate a JSON Resume file. Fails loudly, never silently."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ResumeValidationError(f"Resume JSON file not found: {p}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ResumeValidationError(f"Resume JSON file is not valid JSON: {p} ({exc})") from exc

    # A top-level list or string is valid JSON but not a resume. Without this
    # check the .get() calls below raise AttributeError instead of failing
    # with a message that says what's wrong.
    if not isinstance(data, dict):
        raise ResumeValidationError(
            f"Resume JSON must be a JSON object at the top level, got {type(data).__name__}: {p}"
        )
    resume: dict[str, Any] = data

    basics = data.get("basics") or {}
    if not basics.get("name"):
        raise ResumeValidationError("Resume JSON is missing required field: basics.name")

    work = data.get("work") or []
    if not work:
        raise ResumeValidationError(
            "Resume JSON is missing required field: work (must have at least one entry)"
        )

    return resume
