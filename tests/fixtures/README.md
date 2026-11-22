# Test fixtures

`resume.json` is **synthetic** — a fictitious person, with placeholder
companies, dates, and contact details. No personal data. It exists so
`pytest` passes on a fresh clone without needing anything under
`private-files/`, which is gitignored and local to one machine.

It deliberately differs from `examples/grace-hopper-resume.json`: this one carries
obviously-fake values that make assertions easy to read, while the example
is written to look like a real resume someone would want to produce.

## The ugly characters are deliberate — don't tidy them

`Jane Sámple`, `Sample & Co`, `Montréal`, `team’s`, `<legacy>`, `>40%`,
`"Sample"`, `Research & Development`, `Université` — none of that is
carelessness. The same salting is applied to the `minimal_resume` factory in
`../conftest.py`, which is where most rendering tests get their data.

The reason: a DOCX body is XML, and the renderer once injected resume data
into it unescaped. `R&D` lost its ampersand, and a single `<` terminated the
text node and discarded every section after it — producing a file that opened
in Word without complaint. **57 tests passed over that bug**, because every
fixture used plain ASCII. The suite could not see the failure at all.

Salting the fixtures is what makes ordinary rendering tests catch this class,
instead of relying on someone having written a test for the specific
character that broke. Replacing these with clean ASCII would remove that
coverage without failing anything, which is exactly how the gap appeared the
first time.

**There is no `template.docx` here.** The suite renders against
`examples/resume-template.docx` — the same template users get. A test-only
copy would drift from the shipped one, and the suite would then keep passing
while the published example quietly stopped working. The trade-off is that a
change to the shipped template's tags can fail these tests, which is the
correct outcome: the tags and the context shape have to agree.

The context shape those tags expect is built in
`src/resume_docx/context.py`'s `build_context()`.
