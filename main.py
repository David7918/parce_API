"""
main.py — CLI entry point for Parce.

Usage:
    python main.py <pdf_path> [--output-dir <dir>]
    python main.py --resume <job_id>

Environment variables (via .env):
    LLAMA_CLOUD_API_KEY  — required
    OUTPUT_DIR           — optional, defaults to ./output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from parce.config import load_config
from parce.job_manager import JobManager
from parce.llamaparse_client import LlamaParseClient
from parce.output_manager import derive_output_path, save_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="parce",
        description="Convert a D&D PDF to Markdown using LlamaParse.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "pdf",
        nargs="?",
        metavar="PDF",
        help="Path to the PDF file to convert.",
    )
    group.add_argument(
        "--resume",
        metavar="JOB_ID",
        help="Resume a previously submitted job by its ID.",
    )

    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        help="Directory to write the Markdown file to (overrides OUTPUT_DIR).",
    )

    return parser.parse_args()


def run_new_job(
    pdf_path: Path,
    output_dir: Path,
    client: LlamaParseClient,
    job_manager: JobManager,
) -> None:
    """Upload a PDF, submit a job, poll for completion, and save the result."""

    if not pdf_path.exists():
        raise SystemExit(f"Error: file not found: {pdf_path}")

    if not pdf_path.suffix.lower() == ".pdf":
        raise SystemExit(f"Error: expected a PDF file, got: {pdf_path.name}")

    output_path = derive_output_path(pdf_path, output_dir)

    # --- Upload ---
    print(f"Uploading: {pdf_path.name} …")
    file_id = client.upload_file(pdf_path)
    print(f"Uploaded. File ID: {file_id}")

    # --- Create job ---
    print("Submitting parsing job …")
    job_id = client.create_job(file_id)
    print(f"Job submitted. Job ID: {job_id}")

    # Persist immediately so the job can be resumed if the program is stopped.
    job_manager.save_job(
        job_id=job_id,
        file_id=file_id,
        pdf_path=pdf_path,
        output_path=output_path,
    )

    _finish_job(job_id, output_path, client, job_manager)


def run_resume_job(
    job_id: str,
    client: LlamaParseClient,
    job_manager: JobManager,
) -> None:
    """Resume polling and downloading for an existing job."""
    record = job_manager.get_job(job_id)
    output_path = Path(record["output_path"])

    if record["status"] == "SUCCESS" and output_path.exists():
        print(
            f"Job {job_id} already completed. Output at: {output_path}"
        )
        return

    print(f"Resuming job: {job_id}")
    _finish_job(job_id, output_path, client, job_manager)


def _finish_job(
    job_id: str,
    output_path: Path,
    client: LlamaParseClient,
    job_manager: JobManager,
) -> None:
    """Poll a job and, on success, download and save the Markdown."""
    final_status = job_manager.poll_until_done(job_id, client)

    if final_status != "SUCCESS":
        # Status already saved by poll_until_done — job info is not lost.
        raise SystemExit(
            f"Error: job {job_id} ended with status '{final_status}'.\n"
            "Job record preserved. Check LlamaCloud for details."
        )

    print("Retrieving Markdown …")
    markdown = client.get_markdown(job_id)

    save_markdown(markdown, output_path)
    job_manager.update_status(job_id, "SUCCESS")
    print("Done.")


def main() -> None:
    args = parse_args()
    config = load_config()

    # Allow --output-dir to override the env-configured directory.
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else config.output_dir
    )

    client = LlamaParseClient(api_key=config.api_key)
    job_manager = JobManager(state_file=output_dir / "jobs.json")

    try:
        if args.resume:
            run_resume_job(args.resume, client, job_manager)
        else:
            run_new_job(Path(args.pdf), output_dir, client, job_manager)
    except KeyboardInterrupt:
        print(
            "\nInterrupted. The job is still running on LlamaCloud.\n"
            "Re-run with --resume <job_id> to retrieve the result."
        )
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        # Print a human-readable message; do not expose the API key.
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
