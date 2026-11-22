"""Minimal desktop GUI for resume_docx.generate.

Three fields (input JSON, template DOCX, output DOCX), a Generate button.
No new dependency — tkinter ships with Python's standard library.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox

from resume_docx.generate import generate

FALLBACK_TEMPLATE = Path("examples/resume-template.docx")

ENV_KEYS = ("default_src", "default_out", "default_template")


def _load_env(env_path: Path = Path(".env")) -> dict[str, str]:
    """Read default_src/default_out/default_template from .env, if
    present. No python-dotenv dependency needed for three keys."""
    values = dict.fromkeys(ENV_KEYS, "")
    if not env_path.exists():
        return values
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in values:
            value = value.strip().strip('"').strip("'")
            values[key] = value.replace("\\ ", " ")
    return values


_ENV = _load_env()
# default_out falls back to default_src when unset, per .env.example.
DEFAULT_SRC = _ENV["default_src"]
DEFAULT_OUT = _ENV["default_out"] or DEFAULT_SRC
DEFAULT_TEMPLATE = _ENV["default_template"]


def run_generate(resume_path: str, template_path: str, out_path: str) -> str:
    """Validate the three fields and run the generator. Returns a
    human-readable success message, or raises ValueError with a message
    fit to show the user directly (no UI framework dependency, so this
    stays testable without a display).
    """
    if not resume_path:
        raise ValueError("Choose an input JSON file.")
    if not template_path:
        raise ValueError("Choose a template DOCX file.")
    if not out_path:
        raise ValueError("Choose where to save the output DOCX.")

    generate(resume_path, template_path, out_path)
    return f"Wrote {out_path}"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Resume JSON → DOCX")
        self.resizable(False, False)

        self.resume_var = tk.StringVar()
        self.template_var = tk.StringVar(value=self._initial_template())
        self.out_var = tk.StringVar()

        self._add_row(0, "Input JSON:", self.resume_var, self._browse_resume)
        self._add_row(1, "Template DOCX:", self.template_var, self._browse_template)
        self._add_row(2, "Output DOCX:", self.out_var, self._browse_out)

        generate_btn = tk.Button(self, text="Generate", command=self._on_generate)
        generate_btn.grid(row=3, column=0, columnspan=3, pady=10)

    @staticmethod
    def _initial_template() -> str:
        """default_template (a full file path, from .env) takes priority
        if it exists on disk; falls back to the bundled example template."""
        if DEFAULT_TEMPLATE and Path(DEFAULT_TEMPLATE).exists():
            return DEFAULT_TEMPLATE
        if FALLBACK_TEMPLATE.exists():
            return str(FALLBACK_TEMPLATE)
        return ""

    def _add_row(self, row: int, label: str, var: tk.StringVar, browse_cmd: Callable[[], None]) -> None:
        tk.Label(self, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=var, width=50).grid(row=row, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse...", command=browse_cmd).grid(row=row, column=2, padx=5, pady=5)

    def _browse_resume(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose input JSON",
            initialdir=DEFAULT_SRC or None,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.resume_var.set(path)
            if not self.out_var.get():
                self.out_var.set(str(Path(path).with_suffix(".docx")))

    def _browse_template(self) -> None:
        # If default_template is set, start the browser in its directory
        # rather than default_src — a template usually doesn't live next
        # to resume JSON files.
        template_dir = str(Path(DEFAULT_TEMPLATE).parent) if DEFAULT_TEMPLATE else None
        path = filedialog.askopenfilename(
            title="Choose template DOCX",
            initialdir=template_dir,
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")],
        )
        if path:
            self.template_var.set(path)

    def _browse_out(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save generated DOCX as",
            defaultextension=".docx",
            initialdir=DEFAULT_OUT or None,
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")],
        )
        if path:
            self.out_var.set(path)

    def _on_generate(self) -> None:
        try:
            message = run_generate(self.resume_var.get(), self.template_var.get(), self.out_var.get())
        except ValueError as exc:
            # Covers our own empty-field checks plus generate()'s
            # ResumeValidationError (a ValueError subclass).
            messagebox.showerror("Error", str(exc))
            return
        messagebox.showinfo("Done", message)


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
