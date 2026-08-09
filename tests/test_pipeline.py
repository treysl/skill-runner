from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from runner.inspect import ExportInspection
from runner.pipeline import run_pipeline


def _inspection(path: Path) -> ExportInspection:
    return ExportInspection(
        input_file=str(path),
        row_count=2,
        columns=["Branch"],
        branches=[],
        divisions=[{"value": "Construction", "count": 2}],
        job_statuses=[],
        opportunity_statuses=[],
        missing_required_columns=[],
    )


class PipelineEvidenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_run_returns_manifest_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_file = root / "input.xlsx"
            output_file = root / "CIP_Report_20260809_120000.xlsx"
            manifest_file = root / "manifest.json"
            input_file.touch()
            output_file.touch()
            with (
                patch("runner.pipeline.find_input_file", return_value=input_file),
                patch("runner.pipeline.inspect_export", return_value=_inspection(input_file)),
                patch(
                    "runner.pipeline.orchestrate_build_config",
                    new=AsyncMock(return_value={"divisions": ["Construction"]}),
                ),
                patch(
                    "runner.pipeline.run_build",
                    return_value={"success": True, "output_file": str(output_file)},
                ),
                patch(
                    "runner.evidence.write_success_manifest",
                    return_value=manifest_file,
                ) as write_success,
            ):
                result = await run_pipeline(filename=input_file.name)

            self.assertEqual(result["manifest_file"], str(manifest_file.resolve()))
            write_success.assert_called_once()

    async def test_failed_run_attempts_failure_manifest(self) -> None:
        error = FileNotFoundError("missing")
        with (
            patch("runner.pipeline.find_input_file", side_effect=error),
            patch("runner.evidence.write_failure_manifest") as write_failure,
        ):
            with self.assertRaises(FileNotFoundError):
                await run_pipeline(filename="missing.xlsx")

        write_failure.assert_called_once()
        self.assertIs(write_failure.call_args.kwargs["error"], error)


if __name__ == "__main__":
    unittest.main()
