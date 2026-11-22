#!/usr/bin/env bash
# Launches the desktop GUI (resume_docx.gui).
#
# Usage: ./resume-generator.sh
#
# What the wrapper adds over calling `resume-docx-gui` directly:
#   - Uses .venv's interpreter even when the venv isn't activated.
#   - Checks tkinter up front and prints the right platform-specific fix
#     instead of failing with a raw ImportError.
#   - Runs from the repo root, so the GUI finds .env and the default template
#     (both resolved relative to the working directory).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON="$REPO_ROOT/.venv/bin/python"
else
  echo "Note: .venv not found — falling back to system python3. See README.md for venv setup." >&2
  PYTHON="python3"
fi

if ! "$PYTHON" -c "import tkinter" >/dev/null 2>&1; then
  PYTHON_REAL="$(readlink -f "$PYTHON" 2>/dev/null || echo "$PYTHON")"
  echo "Error: tkinter is not available for $PYTHON." >&2
  if [[ "$PYTHON_REAL" == *".pyenv"* ]]; then
    PYENV_VERSION_STRING=""
    if [ -f "$REPO_ROOT/.venv/pyvenv.cfg" ]; then
      PYENV_VERSION_STRING="$(grep '^version' "$REPO_ROOT/.venv/pyvenv.cfg" | cut -d= -f2 | tr -d ' ')"
    fi
    echo "This is a pyenv-built Python ($PYTHON_REAL) — installing a system tkinter" >&2
    echo "package (e.g. apt/brew) will NOT fix this; tkinter has to be compiled into" >&2
    echo "the Python build itself. Fix:" >&2
    echo "  1. Install Tk headers first: sudo apt install tk-dev   (macOS: brew install tcl-tk)" >&2
    echo "  2. Rebuild the Python version: pyenv install --force ${PYENV_VERSION_STRING:-<your pyenv version, see .venv/pyvenv.cfg>}" >&2
    echo "  3. Recreate the venv: rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -e \".[dev]\"" >&2
  else
    echo "Install it and retry — e.g. on Debian/Ubuntu (including WSL): sudo apt install python3-tk" >&2
    echo "On macOS: brew install python-tk" >&2
  fi
  exit 1
fi

exec "$PYTHON" -c 'from resume_docx.gui import main; main()'
