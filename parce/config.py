"""
config.py — Load and validate runtime configuration.

Reads environment variables (from a .env file if present) and exposes
a single Config dataclass used throughout the application.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (parent of this file's directory).
_ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_FILE)


@dataclass(frozen=True)
class Config:
    api_key: str
    output_dir: Path

    def __str__(self) -> str:
        # Never print the key — show only that it is set.
        return f"Config(api_key=<set>, output_dir={self.output_dir})"


def load_config() -> Config:
    """
    Read configuration from environment variables.

    Raises:
        SystemExit: if LLAMA_CLOUD_API_KEY is not set.
    """
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Error: LLAMA_CLOUD_API_KEY is not set.\n"
            "Copy .env.example to .env and add your API key."
        )

    raw_output_dir = os.environ.get("OUTPUT_DIR", "./output").strip()
    output_dir = Path(raw_output_dir).expanduser().resolve()

    return Config(api_key=api_key, output_dir=output_dir)
