# Architecture Decisions

## ADR-001: Use Python

Decision:
Use Python rather than JavaScript.

Reason:
The project is primarily a local command-line utility and Python
has good support for API interaction and file processing.

Status:
Accepted

---

## ADR-002: Store jobs locally

Decision:
Maintain a local job/state file.

Reason:
Large PDFs may take a significant amount of time to process and
the application should be able to recover from interruption.

Status:
Accepted