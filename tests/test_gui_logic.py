"""Tests for resume_docx.gui's non-UI logic.

This repo's CI/dev environment may not have tkinter installed (it's an
optional stdlib module — see resume-generator.sh's install hint). We stub
tkinter modules before import so these tests exercise run_generate() without
requiring a display or a real Tk installation.
"""

import json
import sys
import types
from pathlib import Path

import docx
import pytest


def _stub_tkinter():
    if "tkinter" in sys.modules and hasattr(sys.modules["tkinter"], "Tk"):
        return  # a real tkinter is already importable; no need to stub

    tk_module = types.ModuleType("tkinter")
    for name in ["Tk", "StringVar", "Label", "Entry", "Button"]:
        setattr(tk_module, name, object)
    sys.modules.setdefault("tkinter", tk_module)
    sys.modules.setdefault("tkinter.filedialog", types.ModuleType("tkinter.filedialog"))
    sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))


_stub_tkinter()

from resume_docx import gui  # noqa: E402  (import after the tkinter stub is installed)

REPO_ROOT = Path(__file__).resolve().parent.parent
# The shipped template — tracked, so it exists on a fresh clone. Deliberately
# not private-files/, which is gitignored and local to one machine.
TEMPLATE = REPO_ROOT / "examples" / "resume-template.docx"


@pytest.mark.parametrize(
    "resume,template,out,expected_substring",
    [
        ("", "t.docx", "o.docx", "input JSON"),
        ("r.json", "", "o.docx", "template"),
        ("r.json", "t.docx", "", "output"),
    ],
)
def test_empty_fields_raise_clear_errors(resume, template, out, expected_substring):
    with pytest.raises(ValueError, match=expected_substring):
        gui.run_generate(resume, template, out)


def test_run_generate_produces_expected_docx(tmp_path):
    resume = {
        "basics": {"name": "Test User"},
        "work": [
            {
                "name": "Acme",
                "location": "X",
                "position": "Eng",
                "startDate": "2020-01",
                "highlights": ["did stuff"],
            }
        ],
    }
    resume_path = tmp_path / "r.json"
    resume_path.write_text(json.dumps(resume), encoding="utf-8")
    out_path = tmp_path / "out.docx"

    message = gui.run_generate(str(resume_path), str(TEMPLATE), str(out_path))

    assert message == f"Wrote {out_path}"
    doc = docx.Document(out_path)
    assert "TEST USER" in [p.text for p in doc.paragraphs]


def test_run_generate_surfaces_validation_errors(tmp_path):
    bad_resume_path = tmp_path / "bad.json"
    bad_resume_path.write_text(json.dumps({"basics": {"name": "X"}}), encoding="utf-8")  # no work[]
    out_path = tmp_path / "out.docx"

    with pytest.raises(ValueError, match="work"):
        gui.run_generate(str(bad_resume_path), str(TEMPLATE), str(out_path))


# --- .env loading (default_src / default_out / default_template) -----------


def write_env(tmp_path, content, name=".env"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_load_env_missing_file_returns_empty(tmp_path):
    result = gui._load_env(tmp_path / "nope.env")
    assert result == {"default_src": "", "default_out": "", "default_template": ""}


def test_load_env_parses_all_three_keys(tmp_path):
    env_path = write_env(
        tmp_path,
        "default_src=/home/jane/resumes\n"
        "default_out=/home/jane/output\n"
        "default_template=/home/jane/templates/base.docx\n",
    )
    result = gui._load_env(env_path)
    assert result == {
        "default_src": "/home/jane/resumes",
        "default_out": "/home/jane/output",
        "default_template": "/home/jane/templates/base.docx",
    }


def test_load_env_ignores_comments_and_blank_lines(tmp_path):
    env_path = write_env(
        tmp_path,
        "# a comment\n\ndefault_src=/x\n# default_out=/should/not/be/used\n",
    )
    result = gui._load_env(env_path)
    assert result["default_src"] == "/x"
    assert result["default_out"] == ""


def test_load_env_ignores_unknown_keys(tmp_path):
    env_path = write_env(tmp_path, "some_other_key=whatever\ndefault_src=/x\n")
    result = gui._load_env(env_path)
    assert result["default_src"] == "/x"
    assert "some_other_key" not in result


def test_load_env_strips_quotes_and_escaped_spaces(tmp_path):
    env_path = write_env(
        tmp_path,
        r'default_src="/mnt/c/Users/Jane\ Doe/Documents"' + "\n",
    )
    result = gui._load_env(env_path)
    assert result["default_src"] == "/mnt/c/Users/Jane Doe/Documents"


def test_load_env_empty_file_returns_empty(tmp_path):
    env_path = write_env(tmp_path, "")
    result = gui._load_env(env_path)
    assert result == {"default_src": "", "default_out": "", "default_template": ""}


# --- Per-field default wiring -----------------------------------------------


def test_initial_template_prefers_default_template_when_it_exists(tmp_path, monkeypatch):
    fake_template = tmp_path / "my-template.docx"
    fake_template.write_text("not a real docx, just needs to exist")
    monkeypatch.setattr(gui, "DEFAULT_TEMPLATE", str(fake_template))
    assert gui.App._initial_template() == str(fake_template)


def test_initial_template_falls_back_when_default_template_path_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(gui, "DEFAULT_TEMPLATE", str(tmp_path / "does-not-exist.docx"))
    monkeypatch.setattr(gui, "FALLBACK_TEMPLATE", TEMPLATE)
    assert gui.App._initial_template() == str(TEMPLATE)


def test_initial_template_falls_back_when_default_template_unset(monkeypatch):
    monkeypatch.setattr(gui, "DEFAULT_TEMPLATE", "")
    monkeypatch.setattr(gui, "FALLBACK_TEMPLATE", TEMPLATE)
    assert gui.App._initial_template() == str(TEMPLATE)


def test_initial_template_empty_when_nothing_available(tmp_path, monkeypatch):
    monkeypatch.setattr(gui, "DEFAULT_TEMPLATE", "")
    monkeypatch.setattr(gui, "FALLBACK_TEMPLATE", tmp_path / "nope.docx")
    assert gui.App._initial_template() == ""


def test_default_out_falls_back_to_default_src_when_unset(tmp_path):
    env_path = write_env(tmp_path, "default_src=/only/src\n")
    result = gui._load_env(env_path)
    default_out = result["default_out"] or result["default_src"]
    assert default_out == "/only/src"


def test_default_out_used_when_set(tmp_path):
    env_path = write_env(tmp_path, "default_src=/src\ndefault_out=/out\n")
    result = gui._load_env(env_path)
    default_out = result["default_out"] or result["default_src"]
    assert default_out == "/out"
