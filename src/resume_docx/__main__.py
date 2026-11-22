"""Entry point for `python -m resume_docx`."""

from __future__ import annotations

import sys

from resume_docx.cli import main

if __name__ == "__main__":
    sys.exit(main())
