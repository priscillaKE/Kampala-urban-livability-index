import unittest

import pandas as pd

from src.index import calculate_livability_index, min_max_normalize


class LivabilityIndexTests(unittest.TestCase):
    def test_normalization_respects_indicator_direction(self):
        values = pd.Series([10, 20, 30])

        self.assertEqual(min_max_normalize(values).tolist(), [0.0, 0.5, 1.0])
        self.assertEqual(
            min_max_normalize(values, higher_is_better=False).tolist(), [1.0, 0.5, 0.0]
        )

    def test_scores_are_weighted_and_ranked(self):
        data = pd.DataFrame(
            {
                "area": ["Central", "North", "South"],
                "access": [10, 20, 30],
                "cost": [100, 50, 25],
            }
        )

        result = calculate_livability_index(
            data,
            indicators=["access", "cost"],
            directions={"access": True, "cost": False},
            weights={"access": 2, "cost": 1},
        )

        self.assertEqual(result.loc[0, "livability_score"], 0.0)
        self.assertEqual(result.loc[2, "livability_score"], 100.0)
        self.assertEqual(result["livability_rank"].tolist(), [3, 2, 1])

    def test_missing_values_report_completeness_and_use_available_weight(self):
        data = pd.DataFrame({"access": [10, None], "green": [0, 10]})

        result = calculate_livability_index(data, ["access", "green"])

        self.assertEqual(result["data_completeness"].tolist(), [1.0, 0.5])
        self.assertEqual(result.loc[1, "livability_score"], 100.0)


if __name__ == "__main__":
    unittest.main()