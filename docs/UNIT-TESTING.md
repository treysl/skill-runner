# Unit Testing

## Scope and approach

The suite uses Python's standard `unittest` framework and targets the runner's
critical decision boundaries:

- input workbook discovery and export inspection;
- conversion of build configuration into safe subprocess arguments;
- successful and failed build-process handling;
- offline orchestration defaults, explicit overrides, and pre-flight rejection;
- packaged skill extraction and cache reuse.
- structured success and failure run manifests;
- neutral output filename generation;
- reconciliation tolerance calculations; and
- reproducibility evidence hashing.

The tests combine **white-box unit testing** (exercising internal branches and
helpers such as JSON extraction and CLI argument construction) with
**black-box unit testing** (asserting observable results and errors from public
functions). Temporary directories isolate filesystem behavior, while mocks
replace Excel parsing, subprocess execution, and external services.

## Run the tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The latest captured execution log is written to
`outputs/unit-test-results.txt`.

## Result

The final run completed **29 tests with 0 failures and 0 errors**. All external
interactions were mocked, so this result specifically verifies unit behavior
rather than network or end-to-end integration behavior.

## Issues discovered and improvements

Testing identified that `find_input_file()` trusted a caller-provided filename.
A value such as `../outside.xlsx` could select a workbook outside `DATA_DIR`,
contrary to the API contract. It also accepted named non-Excel paths and
directories. The implementation now resolves the requested path, verifies it
remains under `DATA_DIR`, requires an `.xlsx` suffix, and requires a regular
file. Regression tests cover all of these boundaries.

The remaining tested paths behaved as intended: missing required export columns
stop orchestration; an empty division selection stops build command creation;
offline orchestration honors explicit overrides; build-process failures retain
stdout/stderr diagnostics; and both flat and nested skill packages are found.

## Types of unit tests

- **Black-box tests** validate inputs and outputs without relying on internal
  implementation details. They protect behavior during refactoring.
- **White-box tests** target known code paths, branches, and error handling.
  They help close coverage gaps that typical usage may not reach.
- **Positive tests** prove valid inputs produce the expected result.
- **Negative tests** prove invalid inputs fail safely and with useful errors.
- **Boundary tests** exercise limits and transitions, such as empty selections,
  missing files, blank spreadsheet values, and paths at a trust boundary.
- **Regression tests** preserve a fix for a previously identified defect so it
  cannot silently return.

## Reliability and modular development

Unit tests make failures deterministic and local: a defect in file selection,
orchestration, or command construction is detected before a full workbook run.
Mocks keep modules independently testable and make the suite fast enough for
frequent execution. Stable contracts between modules allow one component to be
refactored or replaced with immediate feedback if its observable behavior
changes, reducing integration risk and encouraging small, cohesive modules.
