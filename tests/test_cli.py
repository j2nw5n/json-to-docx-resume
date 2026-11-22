"""Tests for resume_docx.cli — argument handling, exit codes, and messages.

The CLI's contract is what a shell script or CI job depends on: a zero exit
and a "Wrote <path>" line on success, a non-zero exit and a stderr message
on bad input. These assert that contract directly rather than through the
`resume-docx` console script, so they don't require an install step.
"""

import pytest

from resume_docx.cli import main


def test_writes_output_and_returns_zero(capsys, tmp_path, template_path, fixture_resume):
    out = tmp_path / "out.docx"
    code = main([str(fixture_resume), "--template", str(template_path), "--out", str(out)])
    assert code == 0
    assert out.exists()
    assert f"Wrote {out}" in capsys.readouterr().out


def test_missing_resume_returns_one_with_stderr_message(capsys, tmp_path, template_path):
    code = main(
        [
            str(tmp_path / "nope.json"),
            "--template",
            str(template_path),
            "--out",
            str(tmp_path / "out.docx"),
        ]
    )
    assert code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "not found" in captured.err
    assert captured.out == ""


def test_validation_error_returns_one_and_writes_nothing(
    capsys, tmp_path, write_resume, template_path, minimal_resume, earlier_experience_entry
):
    resume = write_resume(minimal_resume(work=[earlier_experience_entry(), earlier_experience_entry()]))
    out = tmp_path / "out.docx"
    code = main([str(resume), "--template", str(template_path), "--out", str(out)])
    assert code == 1
    assert not out.exists()
    assert "Earlier Experience" in capsys.readouterr().err


@pytest.mark.parametrize("omit", ["--template", "--out"])
def test_required_flags_are_enforced(tmp_path, template_path, fixture_resume, omit):
    argv = [str(fixture_resume), "--template", str(template_path), "--out", str(tmp_path / "out.docx")]
    index = argv.index(omit)
    del argv[index : index + 2]
    # argparse exits rather than returning, for a usage error.
    with pytest.raises(SystemExit) as excinfo:
        main(argv)
    assert excinfo.value.code == 2


def test_no_arguments_is_a_usage_error():
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
