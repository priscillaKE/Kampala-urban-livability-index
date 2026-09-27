"""Population-based indicator enrichment."""

from __future__ import annotations

import pandas as pd


def add_population_rates(
    indicators: pd.DataFrame,
    population: pd.DataFrame,
    area_key: str = "ADM4_PCODE",
    population_column: str = "population",
    count_prefix: str = "osm_",
) -> pd.DataFrame:
    """Join population and calculate count indicators per 10,000 residents."""
    for frame_name, frame in (("indicators", indicators), ("population", population)):
        if area_key not in frame.columns:
            raise KeyError(f"Missing {area_key} in {frame_name} data")
    if population_column not in population.columns:
        raise KeyError(f"Missing population column: {population_column}")
    if indicators[area_key].duplicated().any():
        raise ValueError(f"Indicator area key must be unique: {area_key}")
    if population[area_key].duplicated().any():
        raise ValueError(f"Population area key must be unique: {area_key}")

    population_values = pd.to_numeric(population[population_column], errors="coerce")
    if population_values.isna().any() or (population_values <= 0).any():
        raise ValueError("Population values must be positive numbers")

    result = indicators.merge(
        population[[area_key, population_column]], on=area_key, how="left", validate="one_to_one"
    )
    if result[population_column].isna().any():
        missing = int(result[population_column].isna().sum())
        raise ValueError(f"Population missing for {missing} indicator area(s)")

    count_columns = [
        column
        for column in result.columns
        if column.startswith(count_prefix) and column.endswith("_count")
    ]
    for column in count_columns:
        result[f"{column}_per_10000"] = (
            result[column] / result[population_column] * 10_000
        ).round(4)
    return result