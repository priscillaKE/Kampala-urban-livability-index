"""Transparent, reusable calculations for the composite livability index."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import pandas as pd


def min_max_normalize(values: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Scale an indicator to 0-1 while preserving missing values.

    A constant indicator receives 0.5 for every observed value because it
    provides no information for differentiating areas.
    """
    numeric = pd.to_numeric(values, errors="coerce")
    minimum = numeric.min()
    maximum = numeric.max()

    if pd.isna(minimum) or minimum == maximum:
        normalized = pd.Series(0.5, index=values.index, dtype="float64")
        normalized[numeric.isna()] = pd.NA
    else:
        normalized = (numeric - minimum) / (maximum - minimum)

    if not higher_is_better:
        normalized = 1 - normalized
    return normalized.astype("Float64")


def calculate_livability_index(
    data: pd.DataFrame,
    indicators: Iterable[str],
    directions: Mapping[str, bool] | None = None,
    weights: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Calculate explainable scores and ranks for geographic areas.

    ``directions`` maps each indicator to whether a higher value is better.
    Missing indicators are excluded from an area's weighted average, while
    ``data_completeness`` reports how much of the requested data was present.
    Scores are returned on a 0-100 scale and are comparable across runs using
    the same indicator data.
    """
    indicator_list = list(indicators)
    if not indicator_list:
        raise ValueError("At least one indicator is required")

    missing_columns = sorted(set(indicator_list) - set(data.columns))
    if missing_columns:
        raise KeyError(f"Missing indicator columns: {', '.join(missing_columns)}")

    directions = directions or {indicator: True for indicator in indicator_list}
    unknown_directions = set(indicator_list) - set(directions)
    if unknown_directions:
        raise KeyError(f"Missing directions for: {', '.join(sorted(unknown_directions))}")

    if weights is None:
        weights = {indicator: 1.0 for indicator in indicator_list}
    unknown_weights = set(indicator_list) - set(weights)
    if unknown_weights:
        raise KeyError(f"Missing weights for: {', '.join(sorted(unknown_weights))}")

    numeric_weights = {indicator: float(weights[indicator]) for indicator in indicator_list}
    if any(weight < 0 for weight in numeric_weights.values()):
        raise ValueError("Weights must be non-negative")
    if sum(numeric_weights.values()) <= 0:
        raise ValueError("At least one weight must be greater than zero")

    result = data.copy()
    normalized_columns: list[str] = []
    for indicator in indicator_list:
        normalized_name = f"{indicator}_normalized"
        result[normalized_name] = min_max_normalize(
            result[indicator], higher_is_better=bool(directions[indicator])
        )
        normalized_columns.append(normalized_name)

    weight_series = pd.Series(numeric_weights)
    normalized = result[normalized_columns].astype("Float64")
    present_weights = normalized.notna().mul(weight_series.values, axis=1)
    result["data_completeness"] = normalized.notna().mean(axis=1)
    scores = (
        normalized.mul(weight_series.values, axis=1).sum(axis=1)
        .div(present_weights.sum(axis=1).replace(0, pd.NA))
        .mul(100)
    )
    result["livability_score"] = scores.astype("Float64").round(2)
    result["livability_rank"] = result["livability_score"].rank(
        ascending=False, method="min", na_option="bottom"
    ).astype("Int64")
    return result