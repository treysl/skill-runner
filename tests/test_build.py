from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runner.build import _safe_name, config_to_cli_args, run_build


class BuildArgumentTests(unittest.TestCase):
    def test_safe_name_removes_path_and_shell_punctuation(self) -> None:
        self.assertEqual(_safe_name("../Acme & Sons"), "___Acme___Sons")
        self.assertEqual(_safe_name("***"), "___")
        self.assertEqual(_safe_name("   "), "Client")

    def test_config_is_translated_to_an_argument_list(self) -> None:
        config = {
            "client_name": "Acme",
            "branches": ["North", "South"],
            "divisions": ["Construction"],
            "completed_range": "ytd",
            "sub_margin": 0.3,
            "user": "tester",
        }
        args = config_to_cli_args(
            config,
            Path("input.xlsx"),
            Path("output.xlsx"),
            Path("build.py"),
        )

        self.assertEqual(args[1:4], ["build.py", "input.xlsx", "output.xlsx"])
        self.assertEqual(args.count("--branch"), 2)
        self.assertIn("Construction", args)
        self.assertIn("--no-logo", args)
        self.assertNotIn("--logo", args)

    def test_at_least_one_division_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least one division"):
            config_to_cli_args(
                {"divisions": []},
                Path("input.xlsx"),
                Path("output.xlsx"),
                Path("build.py"),
            )


class RunBuildTests(unittest.TestCase):
    def test_successful_subprocess_result_is_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "build.py"
            input_file = root / "input.xlsx"
            output_file = root / "nested" / "output.xlsx"
            script.touch()
            input_file.touch()
            completed = subprocess.CompletedProcess(
                args=["python"], returncode=0, stdout="built", stderr=""
            )

            with (
                patch("runner.build.get_build_script", return_value=script),
                patch("runner.build.subprocess.run", return_value=completed) as run,
            ):
                result = run_build(
                    {"client_name": "Acme", "divisions": ["Construction"]},
                    input_file,
                    output_file,
                )

            self.assertTrue(result["success"])
            self.assertEqual(result["stdout"], "built")
            self.assertTrue(output_file.parent.exists())
            run.assert_called_once()
            self.assertIsInstance(run.call_args.args[0], list)

    def test_failed_subprocess_raises_with_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "build.py"
            script.touch()
            completed = subprocess.CompletedProcess(
                args=["python"], returncode=2, stdout="details", stderr="bad input"
            )

            with (
                patch("runner.build.get_build_script", return_value=script),
                patch("runner.build.subprocess.run", return_value=completed),
            ):
                with self.assertRaisesRegex(RuntimeError, "bad input"):
                    run_build(
                        {"divisions": ["Construction"]},
                        root / "input.xlsx",
                        root / "output.xlsx",
                    )


if __name__ == "__main__":
    unittest.main()
