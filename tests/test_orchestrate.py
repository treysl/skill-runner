from __future__ import annotations

import unittest
from unittest.mock import patch

from runner.inspect import ExportInspection
from runner.orchestrate import (
    _apply_runtime_defaults,
    _extract_json,
    orchestrate_build_config,
)


def inspection(*, missing: list[str] | None = None) -> ExportInspection:
    return ExportInspection(
        input_file="sample.xlsx",
        row_count=2,
        columns=[],
        branches=[{"value": "North", "count": 2}],
        divisions=[
            {"value": "Construction", "count": 1},
            {"value": "(blank)", "count": 1},
        ],
        job_statuses=[],
        opportunity_statuses=[],
        missing_required_columns=missing or [],
    )


class OrchestrationHelperTests(unittest.TestCase):
    def test_extract_json_handles_plain_and_fenced_responses(self) -> None:
        self.assertEqual(_extract_json('{"divisions": ["A"]}')["divisions"], ["A"])
        self.assertEqual(
            _extract_json('Result:\n```json\n{"divisions": ["B"]}\n```')["divisions"],
            ["B"],
        )

    def test_runtime_defaults_do_not_replace_explicit_values(self) -> None:
        with patch(
            "runner.orchestrate._load_runtime_config",
            return_value={"completed_range": "ytd", "sub_margin": 0.4},
        ):
            config = _apply_runtime_defaults({"completed_range": "this_month"})

        self.assertEqual(config["completed_range"], "this_month")
        self.assertEqual(config["sub_margin"], 0.4)


class OrchestrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_offline_fallback_uses_observed_divisions_and_overrides(self) -> None:
        with (
            patch("runner.orchestrate.OPENROUTER_API_KEY", ""),
            patch("runner.orchestrate._load_runtime_config", return_value={}),
        ):
            config = await orchestrate_build_config(
                inspection(),
                client_name="Acme",
                user="tester",
                overrides={"sub_margin": 0.33},
            )

        self.assertEqual(config["divisions"], ["Construction"])
        self.assertEqual(config["sub_margin"], 0.33)
        self.assertEqual(config["client_name"], "Acme")
        self.assertEqual(config["user"], "tester")

    async def test_missing_required_columns_stop_orchestration(self) -> None:
        with self.assertRaisesRegex(ValueError, "Revenue Estimated"):
            await orchestrate_build_config(
                inspection(missing=["Revenue Estimated"]),
                client_name="Acme",
                user="tester",
            )


if __name__ == "__main__":
    unittest.main()
