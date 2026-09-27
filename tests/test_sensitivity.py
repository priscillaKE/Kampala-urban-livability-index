import unittest

import pandas as pd

from src.sensitivity import compare_weight_scenarios, rank_stability


class SensitivityTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "area": ["A", "B", "C"],
                "access": [10, 20, 30],
                "cost": [10, 20, 30],
            }
        )

    def test_scenarios_are_kept_in_the_result(self):
        results = compare_weight_scenarios(
            self.data,
            ["access", "cost"],
            {"access": True, "cost": False},
            {
                "balanced": {"access": 1, "cost": 1},
                "access_priority": {"access": 3, "cost": 1},
            },
        )

        self.assertEqual(set(results["scenario"]), {"balanced", "access_priority"})
        self.assertEqual(len(results), 6)

    def test_rank_stability_reports_rank_range(self):
        results = compare_weight_scenarios(
            self.data,
            ["access", "cost"],
            {"access": True, "cost": False},
            {
                "access_priority": {"access": 3, "cost": 1},
                "cost_priority": {"access": 1, "cost": 3},
            },
        )

        summary = rank_stability(results)

        self.assertEqual(summary.loc[summary["area"] == "A", "rank_range"].iloc[0], 2)
        self.assertEqual(summary.loc[summary["area"] == "B", "rank_range"].iloc[0], 0)