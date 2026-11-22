"""Command-line interface.

Reachable three ways, all equivalent:
    resume-docx ...            (console script, from pyproject [project.scripts])
    python -m resume_docx ...  (via __main__.py)
    from resume_docx.cli import main
"""

from __future__ import annotations

import argparse
import sys

from resume_docx.errors import ResumeValidationError
from resume_docx.generate import generate

__all__ = ["main"]

DESCRIPTION = "Generate a styled DOCX resume from a JSON Resume file."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="resume-docx", description=DESCRIPTION)
    parser.add_argument("resume", help="Path to the JSON Resume file")
    parser.add_argument("--template", required=True, help="Path to the Jinja-tagged template DOCX")
    parser.add_argument("--out", required=True, help="Path to write the generated DOCX")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        generate(args.resume, args.template, args.out)
    except ResumeValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
