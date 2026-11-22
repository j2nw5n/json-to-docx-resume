"""Shared exception types.

Live in their own module (rather than in generate.py or a parser module)
so both a resume-format parser and the template-consuming generator can
raise them without importing from each other.
"""

from __future__ import annotations


class ResumeValidationError(ValueError):
    """Raised when the resume data is missing required data."""
