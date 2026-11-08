"""
llamaparse_client.py — Thin wrapper around the llama-cloud SDK.

Responsibilities:
  - Upload a PDF file and return a file ID.
  - Create a parsing job and return a job ID.
  - Fetch the current status of a job.
  - Retrieve the completed Markdown result.
"""

from __future__ import annotations

from pathlib import Path

from llama_cloud import LlamaCloud


class LlamaParseClient:
    """Wraps the LlamaCloud SDK for PDF parsing operations."""

    def __init__(self, api_key: str) -> None:
        # The SDK accepts the key directly; it does not need to come from env.
        self._client = LlamaCloud(token=api_key)

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload_file(self, pdf_path: Path) -> str:
        """
        Upload a PDF to LlamaCloud.

        Args:
            pdf_path: Absolute or relative path to the PDF file.

        Returns:
            The file ID assigned by LlamaCloud.

        Raises:
            FileNotFoundError: if pdf_path does not exist.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with pdf_path.open("rb") as fh:
            file_obj = self._client.files.upload_file(
                upload_file=(pdf_path.name, fh, "application/pdf"),
            )

        return file_obj.id

    # ------------------------------------------------------------------
    # Job lifecycle
    # ------------------------------------------------------------------

    def create_job(self, file_id: str) -> str:
        """
        Submit a parsing job for an already-uploaded file.

        Args:
            file_id: The file ID returned by upload_file().

        Returns:
            The job ID assigned by LlamaCloud.
        """
        job = self._client.parsing.create_job(
            file_id=file_id,
            language=["en"],
        )
        return job.id

    def get_job_status(self, job_id: str) -> str:
        """
        Return the current status string for a job.

        Possible values include: PENDING, SUCCESS, ERROR, CANCELLED.
        """
        job = self._client.parsing.get_job(job_id)
        return job.status.value

    # ------------------------------------------------------------------
    # Result retrieval
    # ------------------------------------------------------------------

    def get_markdown(self, job_id: str) -> str:
        """
        Retrieve the full Markdown output for a completed job.

        Args:
            job_id: The job ID of a successfully completed job.

        Returns:
            The parsed Markdown as a single string.

        Raises:
            RuntimeError: if no Markdown result is available.
        """
        result = self._client.parsing.get_job_result_markdown(job_id)

        pages = getattr(result, "pages", None)
        if not pages:
            raise RuntimeError(
                f"No Markdown pages returned for job {job_id}."
            )

        return "\n\n".join(page.md for page in pages)
