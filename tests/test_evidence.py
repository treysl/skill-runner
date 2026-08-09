from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from runner.evidence import sha256_file, write_failure_manifest, write_success_manifest


class EvidenceManifestTests(unittest.TestCase):
    def test_sha256_file_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.bin"
            path.write_bytes(b"capstone")

            self.assertEqual(
                sha256_file(path),
                "C182DB28DC3E5F090B951513BA90E4001739822317FD0580B315566B85D48B9A",
            )

    def test_success_manifest_records_traceable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_file = root / "input.xlsx"
            output_file = root / "CIP_Report_20260809_120000.xlsx"
            input_file.write_bytes(b"input")
            output_file.write_bytes(b"output")

            with (
                patch(
                    "runner.evidence._workbook_summary",
                    return_value={"worksheet_count": 1, "worksheets": ["Table"]},
                ),
                patch("runner.evidence._git_state", return_value={"commit": "abc", "dirty": False}),
                patch("runner.evidence.SKILL_PACKAGE", input_file),
            ):
                manifest_path = write_success_manifest(
                    input_file=input_file,
                    output_file=output_file,
                    inspection={"row_count": 2, "columns": ["A"], "divisions": []},
                    config={"divisions": ["Construction"]},
                    started_at=datetime(2026, 8, 9, tzinfo=timezone.utc),
                    elapsed_seconds=12.3456,
                    manifest_dir=root / "manifests",
                )

            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["elapsed_seconds"], 12.346)
            self.assertEqual(payload["inspection"]["row_count"], 2)
            self.assertEqual(payload["output"]["filename"], output_file.name)
            self.assertEqual(payload["code"]["commit"], "abc")

    def test_failure_manifest_preserves_error_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = root / "skill.zip"
            skill.write_bytes(b"skill")
            with (
                patch("runner.evidence.SKILL_PACKAGE", skill),
                patch("runner.evidence._git_state", return_value={"commit": None, "dirty": None}),
            ):
                manifest_path = write_failure_manifest(
                    started_at=datetime(2026, 8, 9, tzinfo=timezone.utc),
                    elapsed_seconds=1.0,
                    error=ValueError("bad input"),
                    manifest_dir=root / "manifests",
                )

            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "failure")
            self.assertEqual(payload["error"], {"type": "ValueError", "message": "bad input"})


if __name__ == "__main__":
    unittest.main()
