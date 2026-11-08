"""
output_manager.py — Save parsed Markdown to disk.

Responsibilities:
  - Derive the output filename from the source PDF name.
  - Create the output directory if it does not exist.
  - Write the Markdown file, refusing to silently overwrite existing output.
"""

from __future__ import annotations

from pathlib import Path


def derive_output_path(pdf_path: Path, output_dir: Path) -> Path:
    """
    Return the path where the Markdown file should be written.

    The filename matches the PDF stem with a .md extension.

    Example:
        pdf_path   = /books/phb.pdf
        output_dir = /output
        → /output/phb.md
    """
    return output_dir / (pdf_path.stem + ".md")


def save_markdown(markdown: str, output_path: Path) -> None:
    """
    Write Markdown content to output_path.

    Creates parent directories as needed.

    Args:
        markdown:    The Markdown string to write.
        output_path: The full file path to write to.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Saved: {output_path}")
