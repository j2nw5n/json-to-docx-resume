"""Rendering tests for resume_docx.generate.

Everything here goes through generate() and inspects the resulting DOCX —
run text, run splitting, paragraph styles, list numbering. The data rules
that produce that output are unit-tested in tests/test_context.py; these
prove the template actually renders them.

See tests/fixtures/README.md for the synthetic template/resume used here.
"""

import docx

from resume_docx.generate import generate


def test_fixture_resume_renders_correctly(tmp_path, template_path, fixture_resume):
    """End-to-end render of the shared fixture.

    The fixture is deliberately salted with XML-hostile characters, so these
    assertions double as escaping coverage for every section — the accented
    name through the |upper filter, an ampersand in a job heading, and a "<"
    in a job summary that would otherwise discard the rest of the document.
    """
    out = tmp_path / "out.docx"
    generate(fixture_resume, template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "JANE SÁMPLE" in texts
    assert "Software Engineer — R&D" in texts
    assert "Sample & Co – Montréal, QC – 2022–2024" in texts
    assert "Led a sample team’s roadmap for <legacy> systems." in texts
    assert "Shipped a sample feature that improved a sample metric by >40%." in texts
    assert 'Launched the "Sample" initiative with R&D and Ops.' in texts
    assert "Research & Development:  Docker, Terraform, A/B testing" in texts
    # Education renders last; if any "<" above had escaped its text node,
    # everything after it would be missing.
    assert "Bachelor of Science in Computer Science – Université de Sample – Sample City, ST" in texts


def test_template_file_is_not_modified(tmp_path, template_path, fixture_resume):
    """The template is a style reference, never an output target."""
    before = template_path.read_bytes()
    generate(fixture_resume, template_path, tmp_path / "out.docx")
    assert template_path.read_bytes() == before


def test_skills_bold_run_split_preserved(tmp_path, write_resume, template_path, minimal_resume):
    out = tmp_path / "out.docx"
    generate(write_resume(minimal_resume()), template_path, out)
    line = next(p for p in docx.Document(out).paragraphs if p.text.startswith("Languages"))
    # The category name carries an ampersand, so this also proves escaping
    # survives the bold/plain run split rather than only plain paragraphs.
    assert line.runs[0].text == "Languages & Tools:  "
    assert line.runs[0].bold is True
    assert line.runs[1].text == "Python, Go"


def test_bullets_carry_list_numbering(tmp_path, write_resume, template_path, minimal_resume):
    from docx.oxml.ns import qn

    out = tmp_path / "out.docx"
    generate(write_resume(minimal_resume()), template_path, out)
    bullet = next(p for p in docx.Document(out).paragraphs if p.text == "Shipped a thing.")
    assert bullet._p.find(".//" + qn("w:numPr")) is not None


def test_every_job_gets_its_own_heading(tmp_path, write_resume, template_path, minimal_resume, bare_job):
    """No fixed slot count in the template — six jobs render six headings."""
    out = tmp_path / "out.docx"
    generate(write_resume(minimal_resume(work=[bare_job()] * 6)), template_path, out)
    headings = [p.text for p in docx.Document(out).paragraphs if p.style.name == "Heading 2"]
    assert len(headings) == 6


def test_earlier_experience_renders_heading_and_summary(
    tmp_path, write_resume, template_path, minimal_resume, bare_job, earlier_experience_entry
):
    out = tmp_path / "out.docx"
    resume = write_resume(minimal_resume(work=[bare_job(), earlier_experience_entry()]))
    generate(resume, template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "Earlier Experience" in texts
    assert "Earlier career includes several engineering roles." in texts


def test_no_earlier_experience_omits_heading(tmp_path, write_resume, template_path, minimal_resume):
    out = tmp_path / "out.docx"
    generate(write_resume(minimal_resume()), template_path, out)
    assert "Earlier Experience" not in [p.text for p in docx.Document(out).paragraphs]


def test_empty_skills_omits_heading(tmp_path, write_resume, template_path, minimal_resume):
    out = tmp_path / "out.docx"
    generate(write_resume(minimal_resume(skills=[])), template_path, out)
    assert "Areas of Expertise" not in [p.text for p in docx.Document(out).paragraphs]


def test_no_summary_omits_heading(tmp_path, write_resume, template_path, minimal_resume):
    data = minimal_resume()
    data["basics"].pop("summary", None)
    out = tmp_path / "out.docx"
    generate(write_resume(data), template_path, out)
    assert "Summary" not in [p.text for p in docx.Document(out).paragraphs]


# --- XML-special characters --------------------------------------------------
#
# A DOCX body is XML. Resume data routinely contains "&" (AT&T, R&D) and ">"
# (">50%"), and docxtpl does not escape by default — so these guard a real
# failure mode, not a hypothetical one: unescaped "<" terminates the document
# early and everything after it is silently lost.


def test_ampersand_in_data_survives_rendering(tmp_path, write_resume, template_path, minimal_resume):
    resume = minimal_resume(skills=[{"name": "Research & Development", "keywords": ["A&B"]}])
    resume["work"][0]["name"] = "AT&T"
    out = tmp_path / "out.docx"
    generate(write_resume(resume), template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "Research & Development:  A&B" in texts
    assert any(t.startswith("AT&T – ") for t in texts)


def test_angle_brackets_do_not_truncate_the_document(tmp_path, write_resume, template_path, minimal_resume):
    resume = minimal_resume()
    resume["work"][0]["highlights"] = ["Cut latency by >50%", "Replaced <legacy> pipeline"]
    out = tmp_path / "out.docx"
    generate(write_resume(resume), template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "Cut latency by >50%" in texts
    assert "Replaced <legacy> pipeline" in texts
    # The Education heading comes last in the template; if "<" broke out of the
    # text node, everything after it would be gone.
    assert "Education" in texts


# --- The shipped example ------------------------------------------------------
#
# examples/grace-hopper-resume.json is the first thing a new user runs.
# Nothing else in the suite touches it, so without these it could break
# silently while every other test stayed green.


def test_shipped_example_renders(tmp_path, template_path, example_resume):
    """The README's first command must actually work on a fresh clone."""
    out = tmp_path / "out.docx"
    generate(example_resume, template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "GRACE BREWSTER MURRAY HOPPER" in texts
    # An en-dash in an employer name, straight from the shipped data.
    assert any("Eckert–Mauchly Computer Corporation – " in t for t in texts)
    assert "Earlier Experience" in texts
    assert any(t.startswith("Doctor of Philosophy in Mathematics – ") for t in texts)


def test_shipped_example_renders_every_section(tmp_path, template_path, example_resume):
    """Guards the example's job as a demo: if someone trims it down, the
    features the README advertises stop being demonstrated."""
    out = tmp_path / "out.docx"
    generate(example_resume, template_path, out)
    doc = docx.Document(out)
    texts = [p.text for p in doc.paragraphs]
    for heading in ("Summary", "Areas of Expertise", "Experience", "Education"):
        assert heading in texts, f"example no longer demonstrates the {heading} section"
    jobs = [p for p in doc.paragraphs if p.style.name == "Heading 2"]
    # Five real jobs plus the Earlier Experience heading.
    assert len(jobs) >= 6, "example should show several jobs, to exercise the loop"


def test_template_syntax_in_data_is_not_executed(tmp_path, write_resume, template_path, minimal_resume):
    """Resume data containing Jinja syntax must render literally.

    docxtpl compiles the *template*; data is substituted afterwards and is
    never re-parsed. Asserting it here means a future switch to a two-pass
    render — or to a templating library that behaves differently — fails
    loudly instead of turning resume text into a template-injection vector.
    """
    resume = minimal_resume()
    resume["work"][0]["highlights"] = ["Budget was {{ salary }}", "Used {% raw %} tags"]
    out = tmp_path / "out.docx"
    generate(write_resume(resume), template_path, out)
    texts = [p.text for p in docx.Document(out).paragraphs]
    assert "Budget was {{ salary }}" in texts
    assert "Used {% raw %} tags" in texts
