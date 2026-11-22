# Examples

Two files that together let you generate a resume on a fresh clone without
supplying anything of your own:

| File | What it is |
|------|------------|
| `grace-hopper-resume.json` | A [JSON Resume](https://jsonresume.org/schema/)-formatted sample. |
| `resume-template.docx` | A Jinja-tagged DOCX template, ready to render into. |

Try it:

```bash
./generate.sh examples/grace-hopper-resume.json
```

That writes `output/grace-hopper-resume.docx`.

## About the sample resume

The subject is **Grace Hopper** (1906–1992) — mathematician, compiler
pioneer, and US Navy rear admiral. A historical figure was chosen over a
made-up person so the sample reads like an actual career instead of
`Sample Corp / Sample City, ST`, which makes it much easier to tell whether
your own output looks right.

The employers, dates, roles, and accomplishments are factual. **The summary,
bullet wording, and skills groupings are not** — those are written to
demonstrate what the generator does with each section, not to document her
career. The email and phone number are deliberately non-functional
(`example.com`, a `555` number). Treat the file as illustration, not
biography.

It exercises every feature the generator has: five job blocks with differing
bullet counts, the `Earlier Experience` convention, four skills categories,
three education entries, and a header rendered from `basics`.

## About the template

Formatting lives here, content comes from the JSON. The template holds
Jinja tags (`{{ basics.name|upper }}`, `{%p for job in work %}` … `{%p endfor %}`)
where content should be inserted, and keeps its own fonts, heading styles,
and bullet numbering.

**The template is never modified.** The generator only writes to `--out`.

Copy it and edit the copy in Word to make it yours — retag, restyle, or
rearrange. Keep the tag names matching the context shape built in
`src/resume_docx/context.py`.

It embeds Open Sans (regular, bold, italic, bold-italic), which is most of
the file's size and is why the rendered output looks the same on a machine
that doesn't have the font installed.
