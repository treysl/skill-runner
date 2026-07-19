from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from runner.inspect import REQUIRED_COLUMNS, find_input_file, inspect_export


class FindInputFileTests(unittest.TestCase):
    def test_named_file_must_exist_and_be_xlsx(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            workbook = data_dir / "export.xlsx"
            workbook.touch()

            self.assertEqual(find_input_file(data_dir, "export.xlsx"), workbook.resolve())

            with self.assertRaisesRegex(FileNotFoundError, "File not found"):
                find_input_file(data_dir, "notes.csv")

    def test_named_file_cannot_escape_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            data_dir.mkdir()
            outside = Path(temp_dir) / "outside.xlsx"
            outside.touch()

            with self.assertRaisesRegex(FileNotFoundError, "inside the data folder"):
                find_input_file(data_dir, "../outside.xlsx")

    def test_uses_newest_workbook_when_filename_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            older = data_dir / "older.xlsx"
            newer = data_dir / "newer.xlsx"
            older.touch()
            newer.touch()

            # Use explicit mtimes because glob ordering is not a contract.
            import os

            os.utime(older, (1, 1))
            os.utime(newer, (2, 2))
            self.assertEqual(find_input_file(data_dir), newer)

    def test_raises_when_data_directory_has_no_workbooks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(FileNotFoundError, "No .xlsx files"):
                find_input_file(Path(temp_dir))


class InspectExportTests(unittest.TestCase):
    def test_inspection_reports_counts_blanks_and_missing_columns(self) -> None:
        frame = pd.DataFrame(
            {
                "Branch": ["North", "North", None],
                "Division": ["Construction", "Enhancement", "Construction"],
                "Job Status": ["Open", "Open", "Closed"],
                "Opportunity Status Name": ["Won", "Won", "Pending"],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "sample.xlsx"
            workbook.touch()
            with patch("runner.inspect.pd.read_excel", return_value=frame):
                result = inspect_export(workbook)

        self.assertEqual(result.row_count, 3)
        self.assertEqual(
            result.branches,
            [
                {"value": "North", "count": 2},
                {"value": "(blank)", "count": 1},
            ],
        )
        self.assertIn("Opportunity #", result.missing_required_columns)
        self.assertEqual(
            set(result.missing_required_columns),
            set(REQUIRED_COLUMNS) - set(frame.columns),
        )

    def test_inspection_accepts_an_export_with_all_required_columns(self) -> None:
        frame = pd.DataFrame({column: [None] for column in REQUIRED_COLUMNS})

        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "complete.xlsx"
            workbook.touch()
            with patch("runner.inspect.pd.read_excel", return_value=frame):
                result = inspect_export(workbook)

        self.assertEqual(result.missing_required_columns, [])


if __name__ == "__main__":
    unittest.main()
