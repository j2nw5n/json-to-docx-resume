# Troubleshooting

Environment problems, grouped by what you were doing when it broke. Each
fix is its own block so you can copy it without editing.

## Setup

### `python3 -m venv .venv` fails with "ensurepip is not available"

Debian and Ubuntu (including WSL) ship `venv` separately from Python:

```bash
sudo apt install python3-venv
```

If that package doesn't exist, name your version explicitly:

```bash
sudo apt install python3.12-venv
```

### `python3 -m venv .venv` fails with an `ensurepip` error on WSL

If the repository lives on a Windows-mounted drive (`/mnt/c`, `/mnt/d`),
this happens intermittently. Run the same command again — the retry
succeeds:

```bash
python3 -m venv .venv
```

### Use the project's `.venv`, not a global `python3`

Whatever `python3` resolves to globally may belong to another project, with
packages already installed that mask a missing dependency here, or it may
have no package manager at all. Always create and use the local `.venv`.

### Why install with `.[dev]` rather than `.`

The `[dev]` extra pulls in `pytest`, and running the suite once right after
installing *is* the verification step. It's the fastest way to catch a
missing dependency, a wrong Python version, or a packaging problem, before
it surfaces later as something confusing at runtime.

### Why the `-e` in `pip install -e`

An editable install makes the package importable without reinstalling after
every source change, so the CLI, the GUI, and the test suite all run the
same in-place code.

If you skip `-e`, tests still pass but they'll be testing an installed
snapshot rather than your working tree.

## Running the generator

### `./generate.sh: Permission denied`

Git usually preserves the executable bit, but if it didn't:

```bash
chmod +x generate.sh resume-generator.sh
```

### `ModuleNotFoundError: No module named 'resume_docx'`

The package isn't installed in the interpreter you're using. From the
repository root:

```bash
source .venv/bin/activate && pip install -e ".[dev]"
```

This is also what to run after pulling a change that touches
`pyproject.toml`.

### `Error: no template specified`

`generate.sh` looks for `$TEMPLATE_DOCX`, then
`examples/resume-template.docx`. If neither exists, pass one:

```bash
./generate.sh resume.json path/to/template.docx
```

### Errors mentioning your resume data

Missing required fields, malformed JSON, and a missing template all fail
loudly with a non-zero exit and a message naming the problem. They are not
environment faults — the message says what to fix. For anything about tags
or template structure, see
[template-authoring.md](template-authoring.md#when-something-goes-wrong).

## The GUI

The GUI needs `tkinter`, which ships with Python's standard library but is
packaged separately on some systems. `resume-generator.sh` checks for it up
front and prints the right fix rather than failing with a raw import error.

### System Python on Debian/Ubuntu, including WSL

```bash
sudo apt install python3-tk
```

### System Python on macOS

```bash
brew install python-tk
```

### pyenv-built Python

Check whether this is your situation:

```bash
cat .venv/pyvenv.cfg
```

If the `home` line points into `.pyenv`, **installing a system tkinter
package will not fix it.** pyenv compiles Python from source, and tkinter
has to be compiled in at that point. Three steps, in order.

Install the Tk headers (macOS: `brew install tcl-tk`):

```bash
sudo apt install tk-dev
```

Rebuild the Python version pyenv used, substituting the version from
`pyvenv.cfg`:

```bash
pyenv install --force 3.12.0
```

Recreate the venv so it picks up the rebuild:

```bash
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

### The GUI ignores my `.env` defaults

`.env` and the default template are resolved relative to the current
working directory. Launch from the repository root — `resume-generator.sh`
handles that for you, so prefer it over calling `resume-docx-gui` directly.

## Tests

### Tests fail after changing the template

Expected, and correct. The suite renders against
`examples/resume-template.docx` rather than a private copy, so a tag change
that no longer matches what `build_context()` produces will fail. Fix
whichever of the two is wrong — see
[template-authoring.md](template-authoring.md) for the context shape.

### `pytest` writes files I didn't ask for

Every run regenerates `test-results/` — an HTML report, JUnit XML, and
coverage. The whole directory is gitignored and overwritten each run. To
skip the coverage pass while iterating:

```bash
pytest --no-cov
```
