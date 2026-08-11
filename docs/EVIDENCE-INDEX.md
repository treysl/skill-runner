# Capstone Evidence Index

## Current validation artifacts

| Evidence question | Artifact | Current status |
| --- | --- | --- |
| Is the current evidence ready to share? | `docs/VALIDATION-REPORT.md` | Share with caveats |
| Does the clean test suite pass? | `outputs/unit-test-results.txt` | Verified |
| Does the complete pipeline run? | `docs/BASELINE-VALIDATION-2026-08-09.md` | Verified |
| Are latency and resource use measured? | `docs/PERFORMANCE-EVALUATION.md` | Verified prototype evidence |
| Are historical outputs structurally consistent? | `docs/REPRODUCIBILITY-EVIDENCE.md` | Mixed history; stable current group |
| Do the two latest formal validation outputs share the same structure? | `docs/evidence/structural-reconciliation-latest.json` | PASS, structure only |
| Is each future run traceable? | `runner/evidence.py` | Implemented and live-verified |
| Can an approved reference be compared? | `scripts/reconcile_workbooks.py` | Implemented; reference pending |
| Is manual effort reduction measured? | `docs/EFFICIENCY-EVALUATION-FRAMEWORK.md` | Manual timing pending |

## Primary quantitative evidence

- Latest formal Day 1 validation: 6,989 source rows, 133.818 seconds,
  3,926,024-byte output, and nine worksheets.
- Day 1 system acceptance: four of four checks passed.
- Historical performance baseline: approximately 114 seconds for 6,989 rows.
- Reproducibility inventory: 14 generated workbooks analyzed; 12 match the
  current structural signature.
- Instrumented live run: 87.314 seconds, successful manifest generation, and a
  verified output hash match.

## Evidence boundaries

The repository currently supports claims about successful execution, workbook
structure, input validation, runtime, and repeatable recent construction. It
does not yet support a final claim of financial reconciliation or quantified
analyst time savings. Those claims require the external reference workbook and
manual-process timing respectively.

## Recommended citation order for the capstone

1. Architecture and implementation: `README.md` and source modules.
2. Unit behavior and regression controls: `docs/UNIT-TESTING.md` and
   `outputs/unit-test-results.txt`.
3. End-to-end feasibility: `docs/BASELINE-VALIDATION-2026-08-09.md`.
4. Performance: `docs/PERFORMANCE-EVALUATION.md`.
5. Reproducibility and limitations: `docs/REPRODUCIBILITY-EVIDENCE.md`.
6. Golden-workbook accuracy: add the future reconciliation result.
7. Efficiency: add the completed manual-versus-automated measurement.
