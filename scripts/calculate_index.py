"""Calculate a ranked livability index from an area-level indicator CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.index import calculate_livability_index


def parse_weights(value: str, indicators: list[str]) -> dict[str, float]:
    """Parse ``indicator=value`` pairs, defaulting unspecified weights to 1."""
    weights = {indicator: 1.0 for indicator in indicators}
    if not value:
        return weights
    for item in value.split(","):
        name, separator, weight = item.partition("=")
        if not separator or name not in weights:
            raise ValueError(f"Invalid weight: {item}. Use indicator=value.")
        weights[name] = float(weight)
    return weights


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Area-level indicator CSV")
    parser.add_argument("--output", required=True, help="Output CSV for ranked areas")
    parser.add_argument(
        "--indicators",
        required=True,
        help="Comma-separated indicator columns, for example access,affordability",
    )
    parser.add_argument("--area-column", default="area", help="Area-name column")
    parser.add_argument(
        "--lower-is-better",
        default="",
        help="Comma-separated indicators where lower values are better",
    )
    parser.add_argument(
        "--weights",
        default="",
        help="Optional comma-separated indicator=value pairs",
    )
    args = parser.parse_args()

    indicators = [item.strip() for item in args.indicators.split(",") if item.strip()]
    lower_is_better = {item.strip() for item in args.lower_is_better.split(",") if item.strip()}
    directions = {indicator: indicator not in lower_is_better for indicator in indicators}
    weights = parse_weights(args.weights, indicators)

    data = pd.read_csv(args.input)
    if args.area_column not in data.columns:
        raise KeyError(f"Missing area column: {args.area_column}")

    result = calculate_livability_index(data, indicators, directions, weights)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    print(f"Wrote {len(result)} ranked areas to {output_path}")


if __name__ == "__main__":
    main()