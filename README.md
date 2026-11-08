# Parce

A command-line tool that converts D&D PDF books into Markdown using the
[LlamaParse](https://docs.llamaindex.ai/en/stable/llama_cloud/llama_parse/) API.

Upload a PDF, let LlamaParse process it in the cloud, and get a clean
Markdown file saved locally — without keeping a browser tab open.

---

## Features

- Uploads PDFs to LlamaParse and waits for processing to complete
- Saves the resulting Markdown file locally, named after the source PDF
- Persists job state so a session can be resumed if the program is interrupted
- Reports clear error messages without exposing API credentials

---

## Prerequisites

- Python 3.10 or later
- A [LlamaCloud](https://cloud.llamaindex.ai) account and API key

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/parce.git
cd parce
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your API key:

```
LLAMA_CLOUD_API_KEY=llx-your-actual-key-here
OUTPUT_DIR=./output   # optional, defaults to ./output
```

> **Never commit `.env` to version control.**

---

## Usage

### Convert a PDF

```bash
python main.py path/to/your-book.pdf
```

The Markdown file is saved to the configured output directory with the same
base name as the PDF (e.g. `output/your-book.md`).

### Specify an output directory

```bash
python main.py path/to/your-book.pdf --output-dir ./my-markdown
```

### Resume an interrupted job

If Parce is stopped while a job is running, re-run with the job ID shown
at upload time:

```bash
python main.py --resume <job-id>
```

---

## Project structure

```
parce/
├── parce/
│   ├── __init__.py
│   ├── config.py            # Loads and validates environment variables
│   ├── llamaparse_client.py # LlamaCloud SDK wrapper
│   ├── job_manager.py       # Job state persistence and polling
│   └── output_manager.py    # Saves Markdown to disk
├── main.py                  # CLI entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Development

See [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) for the coding standards followed
in this project.

---

## License

MIT
