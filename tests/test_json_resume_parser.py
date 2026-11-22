"""Unit tests for resume_docx.parsers.json_resume, isolated from anything
template-specific (Earlier Experience) — that lives in resume_docx.generate
and is tested in test_generate.py."""

import json

import pytest

from resume_docx.errors import ResumeValidationError
from resume_docx.parsers.json_resume import parse


def write(tmp_path, data, name="resume.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_parses_valid_resume(tmp_path):
    data = {"basics": {"name": "Jane Doe"}, "work": [{"name": "Acme"}]}
    path = write(tmp_path, data)
    result = parse(path)
    assert result == data


def test_missing_file_fails_loudly(tmp_path):
    with pytest.raises(ResumeValidationError, match="not found"):
        parse(tmp_path / "nope.json")


def test_malformed_json_fails_loudly(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ResumeValidationError, match="not valid JSON"):
        parse(path)


def test_missing_basics_name_fails_loudly(tmp_path):
    path = write(tmp_path, {"work": [{"name": "Acme"}]})
    with pytest.raises(ResumeValidationError, match=r"basics\.name"):
        parse(path)


def test_empty_basics_name_fails_loudly(tmp_path):
    path = write(tmp_path, {"basics": {"name": ""}, "work": [{"name": "Acme"}]})
    with pytest.raises(ResumeValidationError, match=r"basics\.name"):
        parse(path)


def test_missing_work_fails_loudly(tmp_path):
    path = write(tmp_path, {"basics": {"name": "Jane Doe"}})
    with pytest.raises(ResumeValidationError, match="work"):
        parse(path)


def test_empty_work_list_fails_loudly(tmp_path):
    path = write(tmp_path, {"basics": {"name": "Jane Doe"}, "work": []})
    with pytest.raises(ResumeValidationError, match="work"):
        parse(path)


def test_parser_does_not_apply_template_specific_limits(tmp_path):
    """The parser is format-level only — it has no opinion on job count.
    A resume with 10 work entries is valid JSON Resume data; the docxtpl
    template renders any number of jobs, but that's generate()'s concern,
    not this parser's."""
    job = {"name": "a", "startDate": "2020-01"}
    path = write(tmp_path, {"basics": {"name": "Jane Doe"}, "work": [job] * 10})
    result = parse(path)  # must not raise
    assert len(result["work"]) == 10


@pytest.mark.parametrize("payload", ["[]", '"a string"', "42", "null"])
def test_non_object_top_level_fails_loudly(tmp_path, payload):
    """Valid JSON that is not an object used to raise AttributeError from the
    first .get() call — a stack trace instead of a message naming the problem.
    Found by mypy flagging the untyped json.loads() return, not by a test."""
    path = tmp_path / "resume.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ResumeValidationError, match="must be a JSON object"):
        parse(path)
