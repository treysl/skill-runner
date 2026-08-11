from __future__ import annotations

import unittest

from scripts.reconcile_workbooks import _aggregate, compare_values


class ReconciliationCalculationTests(unittest.TestCase):
    def test_numeric_values_pass_within_absolute_tolerance(self) -> None:
        result = compare_values(100.0, 100.005, absolute_tolerance=0.01)
        self.assertTrue(result["passed"])
        self.assertAlmostEqual(result["difference"], 0.005)

    def test_numeric_values_fail_outside_relative_tolerance(self) -> None:
        result = compare_values(100.0, 101.0, relative_tolerance=0.005)
        self.assertFalse(result["passed"])
        self.assertEqual(result["allowed_difference"], 0.5)

    def test_text_values_require_exact_match(self) -> None:
        self.assertTrue(compare_values("Construction", "Construction")["passed"])
        self.assertFalse(compare_values("Construction", "Maintenance")["passed"])

    def test_supported_aggregates(self) -> None:
        values = [1, 2, None, "", 3]
        self.assertEqual(_aggregate(values, "count"), 5)
        self.assertEqual(_aggregate(values, "nonblank_count"), 3)
        self.assertEqual(_aggregate(values, "sum"), 6.0)


if __name__ == "__main__":
    unittest.main()
