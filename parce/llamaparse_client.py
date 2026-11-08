"""
llamaparse_client.py — Thin wrapper around the llama-cloud SDK.

Responsibilities:
  - Upload a PDF file and return a file ID.
  - Create a parsing job and return a job ID.
  - Fetch the current status of a job.
  - Retrieve the completed Markdown result.

Verified against llama-cloud 2.19.0.
"""

from __future__ import annotations

from pathlib import Path

from llama_cloud import LlamaCloud

# Tier controls quality vs. cost. "cost_effective" is a reasonable default
# for large D&D PDFs that contain tables and mixed layouts.
_DEFAULT_TIER = "cost_effective"
_DEFAULT_VERSION = "latest"

# Terminal job statuses — stop polling when any of these appear.
# Source: ParsingGetResponse.job.status Literal annotation.
TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELLED"}


class LlamaParseClient:
    """Wraps the LlamaCloud SDK for PDF parsing operations."""

    def __init__(self, api_key: str) -> None:
        self._client = LlamaCloud(api_key=api_key)

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload_file(self, pdf_path: Path) -> str:
        """
        Upload a PDF to LlamaCloud.

        Args:
            pdf_path: Path to the PDF file (must exist).

        Returns:
            The file ID assigned by LlamaCloud.

        Raises:
            FileNotFoundError: if pdf_path does not exist.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with pdf_path.open("rb") as fh:
            file_obj = self._client.files.create(
                file=(pdf_path.name, fh, "application/pdf"),
                purpose="parse",
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
        job = self._client.parsing.create(
            file_id=file_id,
            tier=_DEFAULT_TIER,
            version=_DEFAULT_VERSION,
        )
        return job.id

    def get_job_status(self, job_id: str) -> str:
        """
        Return the current status string for a job.

        Possible values: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED.
        """
        response = self._client.parsing.get(job_id)
        return response.job.status

    # ------------------------------------------------------------------
    # Result retrieval
    # ------------------------------------------------------------------

    def get_markdown(self, job_id: str) -> str:
        """
        Retrieve the full Markdown output for a completed job.

        Fetches the job with expand=["markdown"] so the Markdown content
        is returned inline rather than as a presigned URL.

        Args:
            job_id: The job ID of a successfully completed job.

        Returns:
            The parsed Markdown as a single string.

        Raises:
            RuntimeError: if no Markdown result is available.
        """
        response = self._client.parsing.get(job_id, expand=["markdown"])

        md = response.markdown
        if not md or not md.pages:
            raise RuntimeError(
                f"No Markdown pages returned for job {job_id}. "
                "The job may not have completed successfully."
            )

        # Each page is either a MarkdownPageMarkdownResultPage (has .markdown)
        # or a MarkdownPageFailedMarkdownPage (has .error). Collect only
        # successful pages and warn about failures.
        parts: list[str] = []
        for page in md.pages:
            if page.success:
                parts.append(page.markdown)
            else:
                print(
                    f"  Warning: page {page.page_number} failed to parse: "
                    f"{getattr(page, 'error', 'unknown error')}"
                )

        if not parts:
            raise RuntimeError(
                f"All pages failed to parse for job {job_id}."
            )

        return "\n\n".join(parts)
