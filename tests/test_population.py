import unittest

import pandas as pd

from src.population import add_population_rates


class PopulationTests(unittest.TestCase):
    def test_adds_rates_per_ten_thousand(self):
        indicators = pd.DataFrame({"ADM4_PCODE": ["A"], "osm_school_count": [50]})
        population = pd.DataFrame({"ADM4_PCODE": ["A"], "population": [1000]})

        result = add_population_rates(indicators, population)

        self.assertEqual(result.loc[0, "osm_school_count_per_10000"], 500.0)

    def test_rejects_missing_population(self):
        indicators = pd.DataFrame({"ADM4_PCODE": ["A", "B"], "osm_school_count": [50, 20]})
        population = pd.DataFrame({"ADM4_PCODE": ["A"], "population": [1000]})

        with self.assertRaisesRegex(ValueError, "Population missing"):
            add_population_rates(indicators, population)

    def test_rejects_duplicate_population_keys(self):
        indicators = pd.DataFrame({"ADM4_PCODE": ["A"], "osm_school_count": [50]})
        population = pd.DataFrame(
            {"ADM4_PCODE": ["A", "A"], "population": [1000, 1100]}
        )

        with self.assertRaisesRegex(ValueError, "must be unique"):
            add_population_rates(indicators, population)