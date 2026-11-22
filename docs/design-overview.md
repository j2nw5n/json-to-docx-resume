# Design overview

How the generator works, for anyone deciding whether to trust it or extend
it.

## The pipeline

Three steps, one per module:

```
resume.json ──▶ parsers/json_resume.py ──▶ context.py ──▶ generate.py ──▶ out.docx
                     parse()               build_context()   render
                  "is this valid        "what can the      docxtpl fills
                   JSON Resume?"         template show?"    the tags
```

`cli.py` wraps that in an argument parser and turns errors into an exit
code. `gui.py` wraps the same `generate()` call in three text fields.
Neither contains generation logic.

## The boundary that matters

The split between `parsers/` and `context.py` is the one deliberate
architectural decision in the codebase, and it exists so two different
kinds of rule stop being tangled:

- **`parsers/json_resume.py`** owns *is this valid JSON Resume data* — file
  reading, JSON decoding, required fields (`basics.name`, a non-empty
  `work[]`). It knows nothing about DOCX, templates, or what any template
  can display.
- **`context.py`** owns *what can this template render* — the
  `Earlier Experience` convention, date-range formatting, which sections
  are optional. These are facts about the template, not about the resume
  format.

Keeping them apart means a template with different capabilities changes
one file, and a new resume format changes the other. Before the split,
both lived in one function and a template constraint was being raised as
a resume-validation error.

## Rendering

Rendering is [docxtpl](https://docxtpl.readthedocs.io/) — Jinja on top of
python-docx. Your template holds tags where content belongs; the generator
builds a context dictionary and renders it. See
[template-authoring.md](template-authoring.md) for the tag reference.

Two consequences worth knowing:

- **There is no job limit.** `{%p for job in work %}` renders as many jobs
  as the data has. Nothing needs to declare a maximum.
- **The template is never modified.** Only `--out` is written. A test
  asserts the template is byte-identical after a render.

Rendering uses `autoescape=True`, which is not optional. A DOCX body is
XML, so unescaped resume data breaks it — `R&D` loses its ampersand, and a
single `<` terminates the text node and discards the rest of the document
while still producing a file that opens cleanly. docxtpl defaults this
off.

## Why docxtpl, and why it wasn't the first choice

The original implementation cloned paragraphs from a reference template by
*index* — paragraph 12 had to be the first job's company line. That worked
for exactly one person's template and broke the moment anyone used their
own.

docxtpl was considered and rejected at that point, for a real reason:
retrofitting Jinja tags into an already-formatted resume without
disturbing its structure is genuinely awkward. That objection didn't
survive the change in goal. Authoring a tagged template *from scratch* is
a different, easier problem, and the concern about nested paragraph loops
— a variable number of bullets inside a loop over jobs — was tested in a
prototype before any commitment. It works.

The migration removed more code than it added, and deleted the fixed
job-slot limit along with the error type that existed to enforce it.

## Extending it

**A new resume format** goes in `parsers/` as a module exposing
`parse(path) -> dict`, returning the JSON Resume shape — which is the
canonical internal representation, so a new format translates into it
rather than introducing its own. `context.py` and `generate.py` need no
changes. A `--format` flag becomes worth adding once a second parser
exists; with one format, a switch would have nothing to switch between.

**A different template layout** is usually not a code change at all —
retag the DOCX. Code changes only if you need a context key that
`build_context()` doesn't produce.
