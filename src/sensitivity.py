"""Sensitivity analysis for composite-index assumptions."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from .index import calculate_livability_index


def compare_weight_scenarios(
    data: pd.DataFrame,
    indicators: list[str],
    directions: Mapping[str, bool],
    scenarios: Mapping[str, Mapping[str, float]],
    area_column: str = "area",
) -> pd.DataFrame:
    """Run the index under named weight scenarios and return long-form results.

    The returned table makes it possible to measure rank stability without
    hiding the assumptions that produced each ranking.
    """
    if area_column not in data.columns:
        raise KeyError(f"Missing area column: {area_column}")
    if not scenarios:
        raise ValueError("At least one weight scenario is required")

    scenario_results: list[pd.DataFrame] = []
    for scenario_name, weights in scenarios.items():
        scored = calculate_livability_index(data, indicators, directions, weights)
        scenario_results.append(
            scored[[area_column, "livability_score", "livability_rank", "data_completeness"]]
            .assign(scenario=scenario_name)
        )

    return pd.concat(scenario_results, ignore_index=True)[
        ["scenario", area_column, "livability_score", "livability_rank", "data_completeness"]
    ]


def rank_stability(results: pd.DataFrame, area_column: str = "area") -> pd.DataFrame:
    """Summarize the rank range and mean rank for each area."""
    required = {area_column, "livability_rank"}
    missing = sorted(required - set(results.columns))
    if missing:
        raise KeyError(f"Missing sensitivity columns: {', '.join(missing)}")

    summary = (
        results.groupby(area_column, as_index=False)["livability_rank"]
        .agg(rank_min="min", rank_max="max", rank_mean="mean")
        .assign(rank_range=lambda frame: frame["rank_max"] - frame["rank_min"])
        .sort_values(["rank_mean", area_column])
    )
    return summary