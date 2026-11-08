# D&D PDF to Markdown Converter

## Purpose

Create a Python application that takes D&D PDF books and converts
them into high-quality Markdown using the LlamaParse API.

## Goal

The application should make it easy to process large D&D PDFs without
having to leave the LlamaParse web UI open.

## Primary User

The DM running the application locally on their computer.

## Core Workflow

1. User selects a PDF.
2. Application uploads it to LlamaParse.
3. Application waits for processing to complete.
4. Application downloads the resulting Markdown.
5. Application saves the Markdown locally.
6. Application reports errors clearly.

## Out of Scope

- Building a PDF parser from scratch.
- Editing the resulting Markdown.
- Building a web interface.
- Automatically publishing the Markdown.

## Technology

- Python
- LlamaParse API
- Local filesystem