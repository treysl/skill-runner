# Golden-Workbook Reconciliation Guide

## Status

The comparison harness is implemented. Final financial reconciliation is
paused until the approved reference workbook is available on this machine.

## Files

- Harness: `scripts/reconcile_workbooks.py`
- Configuration template: `docs/reconciliation-spec.template.json`

## Supported checks

- required worksheet presence;
- worksheet used-range dimensions;
- exact text or identifier cell comparisons;
- numeric cell comparisons with absolute or relative tolerances;
- column sums;
- total row counts; and
- nonblank row counts.

## Preparation

1. Copy `docs/reconciliation-spec.template.json` to a task-specific JSON file.
2. Confirm which workbook is the approved manual reference.
3. Replace the example cells and columns with authoritative acceptance measures.
4. Set tolerances appropriate to each measure. Currency checks will usually use
   a small absolute tolerance; ratios or margins may need a relative tolerance.
5. Keep the reference workbook read-only and record its SHA-256 hash.

The `examples` array in the template is instructional and is not executed. Add
approved checks to the `checks` array.

## Run

```powershell
.\.venv\Scripts\python.exe scripts\reconcile_workbooks.py `
  C:\path\to\approved-reference.xlsx `
  outputs\CIP_Report_YYYYMMDD_HHMMSS.xlsx `
  --spec docs\reconciliation-spec.json `
  --output outputs\reconciliation-result.json
```

The command returns exit code `0` for PASS and `1` for FAIL. A structure-only
run is explicitly labeled as insufficient for financial validation.

## Acceptance gate

Do not state that the automated report financially reconciles until:

- every required worksheet is present;
- every approved value and aggregate check passes within its tolerance;
- all exceptions are explained and approved; and
- the reference, candidate, configuration, code, and skill hashes are retained.
