# Provenance

This project was built by prompting [Claude Code](https://claude.com/claude-code)
— an AI coding agent — rather than by writing the code by hand. This
document says plainly what that means: what was decided by a human, what
was generated, what was actually reviewed, and what was found wrong along
the way. It exists because the honesty is the point, not an afterthought
bolted onto a finished repository.

If you're evaluating this project as a demonstration of skill, this is the
document that says what skill was actually exercised, and where.

## What this project is

A personal experiment in "vibe coding" — building working software by
directing an AI agent through natural-language prompts, deliberately without
reading or writing at the line level, while still holding the result to
real engineering standards: a real test suite, CI, linting, and strict
type checking. The question being tested was not "can an AI write code,"
it was **"can this way of working produce something that would pass review
if a stranger looked at it critically" — and if not, where does it actually
fail.**

The tool itself exists because nothing else did the specific job: take a
[JSON Resume](https://jsonresume.org/) file and a styled DOCX template and
merge them, without hand-reformatting Word every time a resume gets
tailored for a new application. That's a narrow, personal itch — not a
gap in the market being chased, just a tool that didn't exist and was
faster to build than to keep doing by hand.

## What a human actually decided

Not "reviewed the code" — decided the shape of the thing:

- **The templating approach.** Two designs were on the table for making the
  generator work with someone else's template instead of one hardcoded
  paragraph layout: a custom marker syntax, or migrating to
  [docxtpl](https://docxtpl.readthedocs.io/) (Jinja tags in the DOCX). The
  agent's plan document laid out both with tradeoffs; the human chose
  docxtpl, from prior experience with similar Jinja-style templating tools
  elsewhere — not something the agent picked on its own. Recorded verbatim
  on 2026-08-22: *"Per feedback: ... the template-genericization question
  is settled — Option 2 (docxtpl/Jinja templating) ... rather than the
  marker-based Option 1."* See
  [docs/design-overview.md](docs/design-overview.md) for why that decision
  held up.
- **The license.** Apache 2.0 over MIT, also a human call recorded the same
  day, not a default the agent applied.
- **Sequencing.** When to defer public-repo cleanup until the docxtpl
  cutover actually landed, rather than doing both at once — recorded
  2026-08-26: *"Confirmed with the user: ... deferred until the docxtpl
  cutover ... is actually done, not run in parallel."*
- **What ships in `examples/`.** The subject of the sample resume (a
  historical figure, specifically Grace Hopper, chosen from a shortlist),
  and the template itself — `examples/resume-template.docx` was hand-tagged
  in Word by the human, not generated.
- **Every commit and PR merge** along the way. The agent proposed; commits
  and merges to `main` were the human's action.

## The shape of the work

The development history tells a specific story, not a vague "AI helped
write this."

**Day one was a burst, not a trickle.** Of 37 total commits, 18 landed on
the first day (2026-08-21). The very first commit already contains a
301-line `generate.py`, a 243-line test file, and a 261-line design
document — meaning the actual messy, iterative prompting happened before
version control was tracking it, and landed as one working snapshot once
it ran. The fourth commit is titled, plainly, `"Got it working."`

**Then it slows down and becomes deliberate.** After that first day, the
project moved at one or two commits every few days over five weeks
(2026-08-22 through 2026-09-29), each one a named, scoped change — a
feature, a fix, a decision, or a refactor — rather than continued rapid
iteration. That shift from burst to deliberate pacing is itself visible in
the timestamps, not a claim about intent.

**The messy-to-clean arc has numbers, not just a before/after feeling.**
The original `generate.py` was 301 lines doing three jobs at once: argument
parsing, data validation, and paragraph-by-paragraph DOCX cloning keyed to
hardcoded index positions — `paras[0]` had to be the title, `paras[12]` the
first job heading, and so on — that only worked for one specific template
laid out in exactly that order. The equivalent responsibility today is 150
lines split across three single-purpose modules (`generate.py` at 36
lines, `context.py` at 70, `cli.py` at 44). The single commit that made
the templating-engine cutover (2026-08-30) removed 948 lines and added
213 — a net simplification, not a rewrite that grew the codebase.

## What was actually verified, and how

"Vibe coding" is often read as "no verification." That's not what happened
here, and it's checkable:

- **741 lines of tests** across 6 files, all in the published repository.
- **78% line coverage**, enforced with a CI-failing floor (`--cov-fail-under`
  in `pyproject.toml`) — the number is a commitment, not a measurement
  taken once and left to rot.
- **`ruff`, `ruff format --check`, and `mypy --strict`** run on every push
  and pull request, not just locally before a commit.
- **Every module is fully type-annotated**, and the package ships
  `py.typed` — added only after `mypy --strict` passed clean, since
  shipping that marker earlier would have been a claim the code didn't
  support yet.
- **Used in production, not just in tests:** over 30 real resumes
  generated and submitted to real job applications. A broken renderer
  doesn't produce a resume someone can send to an employer, so each one
  is a real pass/fail run against real, non-synthetic data.
- **Setup verified on two separate machines, by the author**, not just
  documented and assumed correct. The environment-setup instructions
  (`.venv` creation, the pyenv/tkinter guidance in
  [docs/troubleshooting.md](docs/troubleshooting.md)) went through
  substantial revision as a direct result of what that second machine
  actually hit.

None of that is a substitute for a human reading every line. It's the
honest alternative to it: behavior is checked mechanically and
continuously, rather than claimed.

## What was found wrong, and who found it

This is the actual test of the method: not whether mistakes happened —
they did — but whether they were caught, and by what.

**Every defect below was found by running or checking the code. None was
found by a human or an AI reading the code and none was caught by the test
suite that was passing at the time.**

| # | Defect | Found by | Tests passing when it was found |
|---|--------|----------|----------------------------------|
| 1 | `docxtpl`'s `autoescape` defaulted to off. A DOCX body is XML, so unescaped resume data corrupted output: `"R&D"` lost its ampersand, and a single `<` silently discarded the rest of the document while producing a file that still opened without complaint. | Rendering a realistic sample resume (Grace Hopper's, containing an ampersand) and reading the result by eye | 57 |
| 2 | `json.loads()`'s untyped return was used unchecked. A file containing valid JSON that wasn't an object — `[]`, `42`, a bare string — crashed with `AttributeError` and a raw stack trace instead of the clear error every other bad input produced. | `mypy --strict`, flagging the untyped return; not a test, not a human reading the parser | 62 |
| 3 | A test asserted `pytest.raises(match="basics.name")`, where `.` is a regex wildcard — the assertion was weaker than it looked, since it would also match `"basicsXname"`. | `ruff`'s `RUF043` lint rule | 62 |

Row 1 is the important one. **57 tests passed over a renderer that
corrupted any resume containing an ampersand**, because every test fixture
used plain ASCII placeholder text — the suite was structurally incapable
of seeing that category of bug. Closing the bug (one line: `autoescape=True`)
was not the same task as closing the gap that let it hide, and both were
done separately: the fixtures were deliberately salted afterward with
en-dashes, curly quotes, accented characters, and ampersands, and a
before/after measurement showed the salting raised the number of tests
that would catch a regression from 2 to 4 — not higher, because most of
the suite correctly asserts structural properties that hostile characters
don't affect.

Rows 2 and 3 matter for a different reason: both are the kind of defect
that's easy to miss by eye — an untyped return, a regex metacharacter
hiding in a plain-looking string — and easy for `mypy --strict` or `ruff`
to catch every time, on every push, without depending on anyone happening
to notice on a given day. That's the actual argument for putting them in
CI rather than treating them as a one-time review step: the goal was a
repeatable, mechanical defense against a whole class of bug, not a single
pass of scrutiny. Rows 2 and 3 are the evidence that the tooling earns its
place — it found real defects, not just style complaints.

## Per-module authorship and review depth

| Module | Authorship | Review depth | What's specifically unverified |
|---|---|---|---|
| `parsers/json_resume.py` | Agent-written, one human-directed bug fix (row 2 above) | Behavior-verified (100% line coverage) | Not read line-by-line since the fix landed |
| `context.py` | Agent-written | Behavior-verified (100% line coverage) | Not read line-by-line |
| `generate.py` | Agent-written, one human-directed bug fix (row 1 above) | Behavior-verified (100% line coverage) | The `docxtpl` library's own internals — depended on, never read |
| `cli.py` | Agent-written | Behavior-verified (96% line coverage) | Not read line-by-line |
| `gui.py` | Agent-written | Partially behavior-verified (60% line coverage — the interactive Tk callbacks aren't exercised by the suite) | The unexercised 40%: file-dialog callbacks, only run by hand, not in CI — addressable with the mocking approach already used elsewhere in this file, not yet done |
| `errors.py` | Agent-written | Behavior-verified (100% line coverage) | Trivial — one exception class |
| `__init__.py` / `__main__.py` | Agent-written | Behavior-verified where exercised | The `__main__` entry point (0% — never invoked by a test, only by hand) |
| Test suite (6 files, 741 lines) | Agent-written, with two files (fixtures) and the salting strategy directed by the failures in the table above | N/A — this is the verification layer itself | The tests are trusted because they pass consistently and were shown to fail against known-bad code (the escaping fix and the fixture salting were both confirmed to fail before the corresponding fix, not just to pass after) |
| `examples/resume-template.docx` | Human-authored, hand-tagged in Word | Audited for personal data (none found) and confirmed byte-unmodified by the generator | Visual correctness confirmed once by eye in Word by the human, not automated |
| CI configuration (`.github/workflows/`) | Agent-written | Verified: both workflows run green on GitHub's own runners across Python 3.10–3.12 | — |

**The honest summary:** behavior is verified continuously and
mechanically. The code's internal implementation — as opposed to its
observable behavior — has not been read line-by-line by the human who
directed its creation, with the exception of the specific bug fixes listed
above, which were reviewed because they were the direct subject of a fix.

## Known unverified

- Whether a *different* person, unfamiliar with this codebase, can
  hand-tag a fresh template in Word without guidance beyond
  [docs/template-authoring.md](docs/template-authoring.md). One person
  (the project's author) has done it once, successfully — that's evidence
  the workflow is possible, not evidence it's easy for a stranger.
- Header and footer tag ergonomics in Word, beyond the one template that's
  been built this way.
- `gui.py`'s interactive code paths (60% covered) are exercised by hand,
  not by CI, so a regression there wouldn't be caught automatically. Not
  an inherent limit — `test_gui_logic.py` already mocks `tkinter`'s
  dialogs for the pure-logic tests, and the same approach would extend to
  the button callbacks. It just hasn't been written yet.

## What this document is not

It is not a claim that AI-written code is equivalent to human-written
code, or that direct behavioral verification standing in for line-by-line
reading holds up past a codebase this size (~400 lines of application
code) or a project this low-stakes. It's a specific account of one small
project, offered instead of silence on how it was actually built.

One honest limit on that account: the dates and quotes cited above come
from the project's real development history, which isn't part of this
repository's own commit log — this copy was published with that history
reset. Take the citations as the author's record, not as something you
can independently verify here.
