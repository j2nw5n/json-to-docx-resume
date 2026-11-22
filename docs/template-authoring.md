# Template authoring

Your template is a normal Word document that keeps its own fonts, heading
styles, margins, and bullet formatting. Where content should appear, it
holds a tag. The generator fills the tags and writes a new file — **your
template is never modified.**

The fastest way to start is to copy the shipped one and edit it:

```bash
cp examples/resume-template.docx my-template.docx
```

Then open `my-template.docx` in Word and change whatever you like. If you'd
rather build from your existing resume, see
[Tagging your own resume](#tagging-your-own-resume) below.

## The two kinds of tag

**`{{ ... }}` substitutes a value** inline, wherever it appears — including
mid-sentence and inside headers and footers.

**`{%p ... %}` is a paragraph-level control tag.** The `p` matters: it tells
docxtpl to remove the entire paragraph containing the tag once it has been
processed, rather than leaving an empty line behind. Use it for `for` and
`if`. Each `{%p for %}` needs a matching `{%p endfor %}` on its own
paragraph, and likewise for `if`/`endif`.

If you use `{% for %}` without the `p`, you get stray blank paragraphs in
your output. That's the single most common mistake.

## Tag reference

Everything available, exactly as `build_context()` in
`src/resume_docx/context.py` produces it.

### Header block

| Tag | Source |
|-----|--------|
| `{{ basics.name }}` | `basics.name` — **required** |
| `{{ basics.label }}` | `basics.label`, e.g. a job title |
| `{{ basics.email }}` | `basics.email` |
| `{{ basics.phone }}` | `basics.phone` |
| `{{ basics.summary }}` | `basics.summary` |

Any other field you put in `basics` is available the same way;
`build_context()` passes the whole object through.

Jinja filters work, so `{{ basics.name|upper }}` renders an all-caps name
without storing it that way in your JSON. The shipped template does this.

Tags work in Word headers and footers — the shipped template puts email and
phone there, separated by tabs.

### Summary — optional section

```
{%p if basics.summary %}
Summary                     ← your Heading 1 paragraph
{{ basics.summary }}
{%p endif %}
```

Wrapping the heading in the `if` is what makes the heading disappear along
with the content. Without it, a resume with no summary renders a lone
"Summary" heading over nothing.

### Skills

`skills` is a list of `{name, keywords}` objects.

```
{%p if skills %}
Areas of Expertise
{%p for category in skills %}
{{ category.name }}:  {{ ', '.join(category.keywords) }}
{%p endfor %}
{%p endif %}
```

`', '.join(...)` renders the keyword list as comma-separated text. To make
the category name bold and the keywords plain, apply the formatting **in
Word to the tag text itself** — bold the `{{ category.name }}:` part and
leave the rest unbolded. The formatting is carried by the run, so it
survives substitution.

### Experience

`work` is a list, one entry per job. Each entry exposes:

| Tag | Notes |
|-----|-------|
| `{{ job.name }}` | Employer |
| `{{ job.location }}` | |
| `{{ job.position }}` | Job title |
| `{{ job.date_range }}` | **Computed**, not from your JSON — see below |
| `{{ job.summary }}` | |
| `{{ job.highlights }}` | A list; loop over it |

```
Experience
{%p for job in work %}
{{ job.name }} – {{ job.location }} – {{ job.date_range }}
{{ job.position }}
{%p if job.summary %}
{{ job.summary }}
{%p endif %}
{%p for highlight in job.highlights %}
{{ highlight }}
{%p endfor %}
{%p endfor %}
```

The nested loop is the important part. Put `{{ highlight }}` on a paragraph
that already uses your bulleted list style, and every bullet inherits that
style and numbering. **There is no limit on jobs or bullets** — the loops
render whatever the data has.

`date_range` is derived from `startDate` and `endDate`, taking the first
four characters of each: `"2020-01"` and `"2022-06"` become `2020–2022`. A
missing `endDate` becomes `2020–Present`. `startDate` is required on every
entry; omitting it is an error, not a blank.

### Earlier Experience — optional

For older roles you'd rather summarize than list, add **one** `work[]` entry
named exactly `Earlier Experience`. It is pulled out of `work` and exposed
separately, so it renders as a heading plus one paragraph with no title,
bullets, or dates:

```
{%p if earlier_experience %}
Earlier Experience
{{ earlier_experience.summary }}
{%p endif %}
```

`summary` is required on that entry. More than one such entry is an error
rather than a silent pick.

### Education

`education` is a list of JSON Resume education objects, passed through
unchanged — so `studyType`, `area`, `institution`, `location`, and any other
field you include are all available.

```
{%p if education %}
Education
{%p for edu in education %}
{{ edu.studyType }} in {{ edu.area }} – {{ edu.institution }} – {{ edu.location }}
{%p endfor %}
{%p endif %}
```

## Tagging your own resume

You can convert an existing resume instead of starting from the example.
It's mechanical, but do it on a copy.

1. Copy your resume to a new file and delete the content you want to come
   from JSON, leaving the headings and one representative paragraph of each
   repeating kind — one job block, one bullet, one skills line.
2. Replace the text in each remaining paragraph with the matching tag,
   keeping the paragraph's style. Type tags directly in Word; don't paste
   from a text editor, or autocorrect may convert the quotes.
3. Add the `{%p for %}` / `{%p endfor %}` pairs around each repeating
   paragraph, each on its own line.
4. Wrap optional sections, headings included, in `{%p if %}` / `{%p endif %}`.
5. Render it and check the output.

```bash
./generate.sh examples/grace-hopper-resume.json my-template.docx
```

Using the example data here rather than your own is deliberate: it has
several jobs with differing bullet counts and an `Earlier Experience`
entry, so it exercises the loops harder than a single-job file would.

## When something goes wrong

**Blank paragraphs between jobs or bullets** — a control tag is missing its
`p`: `{% for %}` instead of `{%p for %}`.

**`TemplateSyntaxError`** — an unclosed tag, or Word's autocorrect turned
a straight quote into a curly one inside a tag. Retype the tag in Word.

**A section renders its heading with nothing under it** — the heading is
outside the `{%p if %}`. Move it inside.

**Formatting lost on a substituted value** — the tag spans two runs with
different formatting. Delete the tag and retype it in one go so it lives in
a single run.

**Nothing changed in the output** — check you're opening the `--out` file.
The template is never written to.
