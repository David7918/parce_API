# Requirements

## Input

- Accept PDF files.
- PDFs may be several hundred pages.
- PDFs may contain images, tables, and multiple columns.

## Processing

- Upload the PDF to LlamaParse.
- Use the Markdown output format.
- Poll for completion rather than assuming processing is immediate.
- Handle API failures.
- Handle network interruptions.

## Output

- Save the resulting Markdown using the PDF's filename.
- Preserve the original PDF.
- Save output to a configurable directory.

## User Experience

- Display processing progress.
- Display useful error messages.
- Do not require the user to manually interact with a browser.

## Reliability

- If the program is interrupted while processing, it should be possible
  to determine whether the job can be resumed.