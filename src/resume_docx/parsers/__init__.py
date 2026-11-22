"""Resume format parsers.

Each parser module owns everything about whether a file is valid data for
its format — reading, decoding, and that format's own required fields. A
parser knows nothing about what any particular DOCX template can render
(job-count limits, template-specific conventions like "Earlier Experience"
— those live with the template-consuming code, not here).

Contract: a parser module exposes `parse(path) -> dict`, returning data in
the JSON Resume shape (`basics`/`work`/`education`/`skills`), which is the
canonical internal representation `resume_docx.generate` consumes — even
for a hypothetical future non-JSON-Resume format, whose parser would
translate into this same shape rather than inventing a new one.

Currently only one format is implemented: json_resume.
"""
