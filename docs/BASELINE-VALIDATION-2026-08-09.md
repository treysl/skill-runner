# Release-Candidate Baseline Validation

**Project:** Deterministic Skill-Runner for Reporting Pipeline

**Validation date:** 2026-08-09

**Git branch:** `main`

**Source commit:** `ab414c0800d05b5a553de8b85bf2cc5483ef6587`

## Outcome

The clean-environment, live-service, and end-to-end validation passed. The
prototype processed the anonymized source workbook through the active n8n
workflow, local FastAPI runner, packaged CIP skill, and deterministic workbook
builder. The newly generated workbook then passed all system acceptance checks.

| Gate | Result | Evidence |
| --- | --- | --- |
| Clean Python environment | PASS | Recreated `.venv` with Python 3.12.13 and installed `requirements.txt` |
| Unit tests | PASS | 18/18 passed in 0.060 seconds |
| Runner health | PASS | `GET /health` returned `{"status":"ok"}` |
| n8n workflow | PASS | Workflow `B2OhEXFayiT3fKNG` synced and activated |
| End-to-end pipeline | PASS | n8n webhook returned `status: success` |
| System acceptance | PASS | AT-01 through AT-04 passed |

## End-to-end run

| Field | Measured result |
| --- | --- |
| Start time | 2026-08-09 11:21:39 CDT |
| Elapsed time | 133.818 seconds |
| Input | `data/Anonymized_Opportunity.xlsx` |
| Input rows | 6,989 |
| Missing required columns | None |
| Selected division | Construction |
| Construction rows observed | 1,272 |
| Completed window | Year to date |
| Output | `outputs/THG_CIP_Report_20260809_112243.xlsx` |
| Output size | 3,926,024 bytes |
| Output worksheets | 9 |
| AI-use disclaimer returned | Yes |

The output contains the expected worksheets: Proprietary Disclosure,
Dashboard, In Process, In Process By Property, Completed, Completed Dashboard
View, Complete Overview, Table, and Version History. The Table worksheet
contains 6,990 rows including its header and 111 columns.

## System acceptance results

| ID | Check | Result |
| --- | --- | --- |
| AT-01 | API health | PASS |
| AT-02 | Data inventory | PASS |
| AT-03 | Workbook opens and required sheets exist | PASS |
| AT-04 | Unsafe traversal request is rejected | PASS |

## Artifact integrity

SHA-256 values make the validation inputs, skill package, and output uniquely
identifiable.

| Artifact | SHA-256 |
| --- | --- |
| Anonymized input | `BCE904040FD0B198FC2AD6F21B6E0362DD84F88F4DC2F61248D5FED511FFB534` |
| Packaged CIP skill | `2F88FEF793298508A46960E6747455EB0670A039B24038F91CC3BE7E1AC16304` |
| Generated output | `46089BA6F9A57783C8670FC674385F12828FAF05648462B40BE462406440A230` |

## Environment snapshot

| Component | Version |
| --- | --- |
| Python | 3.12.13 |
| FastAPI | 0.141.1 |
| Uvicorn | 0.52.1 |
| HTTPX | 0.28.1 |
| pandas | 3.0.5 |
| openpyxl | 3.1.5 |
| NumPy | 2.5.2 |

## Release-candidate interpretation

This run establishes a current, reproducible prototype baseline and confirms
that the primary capstone demonstration path works. It does not claim
production readiness. Golden-workbook financial reconciliation, expanded run
manifests, authentication, structured logging, and production security review
remain separate closeout or future-hardening activities.
