"""Unit tests for resume_docx.context.build_context.

These cover the template-shaped rules — the "Earlier Experience"
convention, date-range formatting, and how missing sections are passed
through — directly against the context dict, with no DOCX rendering
involved. The rendering side of the same behavior lives in
tests/test_generate.py.
"""

import pytest

from resume_docx.context import EARLIER_EXPERIENCE_NAME, build_context
from resume_docx.errors import ResumeValidationError

# --- Job partitioning -------------------------------------------------------


def test_real_jobs_and_earlier_experience_are_separated(minimal_resume, bare_job, earlier_experience_entry):
    resume = minimal_resume(work=[bare_job(), earlier_experience_entry()])
    context = build_context(resume)
    assert len(context["work"]) == 1
    assert context["work"][0]["name"] == "a"
    assert context["earlier_experience"]["name"] == EARLIER_EXPERIENCE_NAME


def test_earlier_experience_is_none_when_absent(minimal_resume):
    assert build_context(minimal_resume())["earlier_experience"] is None


def test_no_job_count_limit(minimal_resume, bare_job):
    """No MAX_REAL_JOBS-style fixed slot count — the Jinja loop takes any number."""
    context = build_context(minimal_resume(work=[bare_job()] * 25))
    assert len(context["work"]) == 25


# --- Date ranges ------------------------------------------------------------


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("2020-01", "2022-01", "2020–2022"),
        ("2020-01-15", "2022-12-31", "2020–2022"),
        ("2020", "2022", "2020–2022"),
        ("2020-01", None, "2020–Present"),
        ("2020-01", "", "2020–Present"),
    ],
)
def test_date_range_formatting(minimal_resume, bare_job, start, end, expected):
    resume = minimal_resume(work=[bare_job(startDate=start, endDate=end)])
    assert build_context(resume)["work"][0]["date_range"] == expected


def test_missing_start_date_fails_loudly(minimal_resume, bare_job):
    job = bare_job()
    del job["startDate"]
    with pytest.raises(ResumeValidationError, match="startDate"):
        build_context(minimal_resume(work=[job]))


# --- Earlier Experience validation ------------------------------------------


def test_duplicate_earlier_experience_fails_loudly(minimal_resume, earlier_experience_entry):
    resume = minimal_resume(work=[earlier_experience_entry(), earlier_experience_entry()])
    with pytest.raises(ResumeValidationError, match=EARLIER_EXPERIENCE_NAME):
        build_context(resume)


def test_earlier_experience_missing_summary_fails_loudly(minimal_resume, bare_job, earlier_experience_entry):
    entry = earlier_experience_entry()
    del entry["summary"]
    with pytest.raises(ResumeValidationError, match="summary"):
        build_context(minimal_resume(work=[bare_job(), entry]))


def test_earlier_experience_name_is_matched_after_stripping(minimal_resume, earlier_experience_entry):
    resume = minimal_resume(work=[earlier_experience_entry(name="  Earlier Experience  ")])
    assert build_context(resume)["earlier_experience"] is not None


# --- Optional sections ------------------------------------------------------


@pytest.mark.parametrize("key", ["skills", "education"])
def test_optional_sections_default_to_empty_list(minimal_resume, key):
    resume = minimal_resume()
    del resume[key]
    assert build_context(resume)[key] == []


@pytest.mark.parametrize("key", ["skills", "education"])
def test_optional_sections_null_becomes_empty_list(minimal_resume, key):
    assert build_context(minimal_resume(**{key: None}))[key] == []


def test_missing_highlights_becomes_empty_list(minimal_resume, bare_job):
    context = build_context(minimal_resume(work=[bare_job()]))
    assert context["work"][0]["highlights"] == []
