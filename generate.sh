#!/usr/bin/env bash
# Convenience wrapper around the `resume-docx` console script.
#
# Usage:
#   ./generate.sh <resume.json> [template.docx]
#
# What the wrapper adds over calling `resume-docx` directly:
#   - Uses .venv's interpreter even when the venv isn't activated.
#   - Defaults the template ($TEMPLATE_DOCX, else the bundled example).
#   - Defaults the output path to output/<resume-basename>.docx.
#
# For full control over the output path, call the console script directly:
#   resume-docx resume.json --template template.docx --out resume.docx

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <resume.json> [template.docx]" >&2
  exit 1
fi

RESUME_JSON="$1"

if [ "$#" -eq 2 ]; then
  TEMPLATE_DOCX="$2"
elif [ -n "${TEMPLATE_DOCX:-}" ]; then
  : # use the value already exported in the environment
elif [ -f "examples/resume-template.docx" ]; then
  TEMPLATE_DOCX="examples/resume-template.docx"
else
  echo "Error: no template specified and examples/resume-template.docx is missing." >&2
  echo "Pass one explicitly: $0 $RESUME_JSON path/to/template.docx" >&2
  echo "Or set TEMPLATE_DOCX in your environment." >&2
  exit 1
fi

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON="$REPO_ROOT/.venv/bin/python"
else
  echo "Note: .venv not found — falling back to system python3. See README.md for venv setup." >&2
  PYTHON="python3"
fi

mkdir -p output
OUT_PATH="output/$(basename "$RESUME_JSON" .json).docx"

exec "$PYTHON" -m resume_docx "$RESUME_JSON" --template "$TEMPLATE_DOCX" --out "$OUT_PATH"
