"""
job_manager.py — Persist and manage LlamaParse job state.

Responsibilities:
  - Write job metadata to jobs.json so the application can survive restarts.
  - Poll for job completion with a simple status loop.
  - Support resuming a previously submitted job by ID.

Job record schema:
  {
    "job_id":     str,
    "file_id":    str,
    "pdf_path":   str,       # original PDF path (absolute)
    "output_path": str,      # where the .md file will be written
    "status":     str,       # last known status
    "created_at": str        # ISO-8601 timestamp
  }
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parce.llamaparse_client import LlamaParseClient

# How long to wait between status checks (seconds).
POLL_INTERVAL = 10

# Terminal statuses — stop polling when any of these appear.
TERMINAL_STATUSES = {"SUCCESS", "ERROR", "CANCELLED"}


class JobManager:
    """Reads and writes job state from a local jobs.json file."""

    def __init__(self, state_file: Path) -> None:
        self._state_file = state_file
        self._jobs: dict[str, dict] = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, dict]:
        """Load existing jobs from disk, returning an empty dict if absent."""
        if self._state_file.exists():
            with self._state_file.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _save(self) -> None:
        """Write current job state to disk atomically."""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._state_file.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(self._jobs, fh, indent=2)
        tmp.replace(self._state_file)

    # ------------------------------------------------------------------
    # Job records
    # ------------------------------------------------------------------

    def save_job(
        self,
        job_id: str,
        file_id: str,
        pdf_path: Path,
        output_path: Path,
    ) -> None:
        """Create or overwrite a job record and persist it."""
        self._jobs[job_id] = {
            "job_id": job_id,
            "file_id": file_id,
            "pdf_path": str(pdf_path.resolve()),
            "output_path": str(output_path.resolve()),
            "status": "PENDING",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()

    def update_status(self, job_id: str, status: str) -> None:
        """Update the status of an existing job and persist."""
        if job_id not in self._jobs:
            raise KeyError(f"Unknown job ID: {job_id}")
        self._jobs[job_id]["status"] = status
        self._save()

    def get_job(self, job_id: str) -> dict:
        """
        Return the stored record for job_id.

        Raises:
            KeyError: if job_id is not in the state file.
        """
        if job_id not in self._jobs:
            raise KeyError(
                f"Job '{job_id}' not found in {self._state_file}.\n"
                "Check the job ID and try again."
            )
        return self._jobs[job_id]

    def all_jobs(self) -> list[dict]:
        """Return all stored job records."""
        return list(self._jobs.values())

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def poll_until_done(
        self,
        job_id: str,
        client: "LlamaParseClient",
    ) -> str:
        """
        Poll LlamaParse until the job reaches a terminal status.

        Args:
            job_id: The job to poll.
            client: A LlamaParseClient instance.

        Returns:
            The final status string (e.g. "SUCCESS" or "ERROR").
        """
        print(f"Polling job {job_id} …")

        while True:
            status = client.get_job_status(job_id)
            self.update_status(job_id, status)
            print(f"  Status: {status}")

            if status in TERMINAL_STATUSES:
                return status

            time.sleep(POLL_INTERVAL)
