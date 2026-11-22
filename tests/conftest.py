"""Shared fixtures for the test suite.

Exposed as pytest fixtures rather than importable module-level helpers so
test files don't have to import from each other (or rely on pytest putting
tests/ on sys.path).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def template_path() -> Path:
    """The shipped template, deliberately the same file users get rather than
    a test-only copy — a second copy under fixtures/ would drift, and then the
    suite would pass while the published example quietly stopped working."""
    return REPO_ROOT / "examples" / "resume-template.docx"


@pytest.fixture
def fixture_resume() -> Path:
    """The synthetic JSON Resume that pairs with template_path. Deliberately
    salted with XML-hostile characters — see tests/fixtures/README.md."""
    return FIXTURES / "resume.json"


@pytest.fixture
def example_resume() -> Path:
    """The resume shipped in examples/ — the first thing a new user runs."""
    return REPO_ROOT / "examples" / "grace-hopper-resume.json"


@pytest.fixture
def write_resume(tmp_path: Path) -> Callable[..., Path]:
    """Write resume data to a temp .json file and return its path."""

    def _write(data: dict[str, Any], name: str = "resume.json") -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return _write


@pytest.fixture
def minimal_resume() -> Callable[..., dict[str, Any]]:
    """A valid resume exercising every section the template renders.
    Keyword overrides replace top-level keys.

    Values carry XML-hostile characters on purpose — an ampersand in the
    employer and in a skills category, an umlaut in the location. Most
    rendering tests build their data here, so escaping gets exercised
    incidentally by all of them rather than only by the tests written for
    it. Keep it that way; a "tidy-up" to plain ASCII would silently remove
    that coverage."""

    def _build(**overrides: Any) -> dict[str, Any]:
        data: dict[str, Any] = {
            "basics": {
                "name": "Jane Doe",
                "label": "Engineer",
                "email": "jane@example.com",
                "phone": "555-1234",
            },
            "work": [
                {
                    "name": "Acme & Sons",
                    "location": "Zürich",
                    "position": "Eng",
                    "startDate": "2020-01",
                    "endDate": "2022-01",
                    "summary": "Did engineering things.",
                    "highlights": ["Shipped a thing.", "Fixed a bug."],
                }
            ],
            "skills": [{"name": "Languages & Tools", "keywords": ["Python", "Go"]}],
            "education": [
                {
                    "studyType": "Bachelor of Science",
                    "area": "Computer Science",
                    "institution": "State U",
                    "location": "Springfield",
                }
            ],
        }
        data.update(overrides)
        return data

    return _build


@pytest.fixture
def bare_job() -> Callable[..., dict[str, Any]]:
    """The smallest work[] entry that passes validation."""

    def _build(**overrides: Any) -> dict[str, Any]:
        job = {"name": "a", "location": "x", "position": "y", "startDate": "2020-01"}
        job.update(overrides)
        return job

    return _build


@pytest.fixture
def earlier_experience_entry() -> Callable[..., dict[str, Any]]:
    """A work[] entry using the "Earlier Experience" convention."""

    def _build(**overrides: Any) -> dict[str, Any]:
        entry = {
            "name": "Earlier Experience",
            "position": "",
            "startDate": "1996",
            "endDate": "2010",
            "summary": "Earlier career includes several engineering roles.",
        }
        entry.update(overrides)
        return entry

    return _build
