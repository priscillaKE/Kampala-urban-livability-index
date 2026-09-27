"""Join a documented population table to processed area indicators."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.population import add_population_rates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--indicators", required=True)
    parser.add_argument("--population", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--area-key", default="ADM4_PCODE")
    parser.add_argument("--population-column", default="population")
    parser.add_argument("--population-source", required=True)
    parser.add_argument("--population-date", required=True)
    args = parser.parse_args()

    indicators = pd.read_csv(args.indicators)
    population = pd.read_csv(args.population)
    result = add_population_rates(
        indicators,
        population,
        area_key=args.area_key,
        population_column=args.population_column,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    metadata = {
        "indicator_input": args.indicators,
        "population_input": args.population,
        "population_source": args.population_source,
        "population_date": args.population_date,
        "area_key": args.area_key,
        "population_column": args.population_column,
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "area_count": len(result),
        "output": str(output_path),
    }
    metadata_path = output_path.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote population-adjusted indicators for {len(result)} areas to {output_path}")


if __name__ == "__main__":
    main()