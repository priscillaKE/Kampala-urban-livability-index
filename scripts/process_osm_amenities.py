"""Aggregate downloaded OSM amenities to ADM2 areas."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Raw OSM GeoJSON")
    parser.add_argument("--boundaries", required=True, help="ADM2 boundary shapefile")
    parser.add_argument("--output", required=True, help="Processed area GeoJSON")
    parser.add_argument("--area-column", default="ADM2_EN")
    parser.add_argument("--parent-column", help="Optional parent geography column")
    parser.add_argument("--parent-value", help="Value to retain in the parent geography")
    args = parser.parse_args()

    raw = gpd.read_file(args.input)
    boundaries = gpd.read_file(args.boundaries)
    if raw.crs is None:
        raise ValueError("OSM input has no CRS")
    if boundaries.crs is None:
        raise ValueError("Boundary input has no CRS")
    if args.area_column not in boundaries.columns:
        raise KeyError(f"Missing area column: {args.area_column}")
    if boundaries[args.area_column].duplicated().any():
        raise ValueError(f"Area column must be unique: {args.area_column}")
    if bool(args.parent_column) != bool(args.parent_value):
        raise ValueError("--parent-column and --parent-value must be supplied together")
    if args.parent_column:
        if args.parent_column not in boundaries.columns:
            raise KeyError(f"Missing parent column: {args.parent_column}")
        boundaries = boundaries[boundaries[args.parent_column].eq(args.parent_value)].copy()
        if boundaries.empty:
            raise ValueError(f"No boundaries found for {args.parent_column}={args.parent_value}")
        boundaries = boundaries.reset_index(drop=True)

    # Representative points are calculated in a metric CRS to avoid geographic
    # centroid warnings and then transformed back for the spatial join.
    projected = raw.to_crs("EPSG:32636")
    points = projected.geometry.representative_point().to_crs("EPSG:4326")
    point_features = gpd.GeoDataFrame(raw.drop(columns="geometry"), geometry=points, crs="EPSG:4326")
    boundaries_wgs84 = boundaries.to_crs("EPSG:4326")
    joined = gpd.sjoin(
        point_features,
        boundaries_wgs84[[args.area_column, "geometry"]],
        how="left",
        predicate="within",
    )

    joined["category"] = joined["amenity"].where(
        joined.get("amenity", pd.Series(index=joined.index)).notna(),
        joined.get("leisure", pd.Series(index=joined.index)),
    )
    counts = (
        joined.dropna(subset=[args.area_column])
        .pivot_table(index=args.area_column, columns="category", values="geometry", aggfunc="count", fill_value=0)
        .reset_index()
    )
    count_columns = [column for column in counts.columns if column != args.area_column]
    counts["osm_feature_count"] = counts[count_columns].sum(axis=1) if count_columns else 0
    counts = counts.rename(
        columns={
            "school": "osm_school_count",
            "hospital": "osm_hospital_count",
            "park": "osm_park_count",
        }
    )

    result = boundaries_wgs84.merge(counts, on=args.area_column, how="left")
    numeric_columns = [column for column in result.columns if column.startswith("osm_")]
    result[numeric_columns] = result[numeric_columns].fillna(0).astype(int)
    boundary_metric = boundaries_wgs84.to_crs("EPSG:32636")
    result["area_km2"] = (boundary_metric.geometry.area.to_numpy() / 1_000_000).round(4)
    density_columns: list[str] = []
    for column in numeric_columns:
        density_column = f"{column}_per_km2"
        result[density_column] = (result[column] / result["area_km2"]).round(4)
        density_columns.append(density_column)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_file(output_path, driver="GeoJSON")
    csv_path = output_path.with_suffix(".csv")
    result.drop(columns="geometry").to_csv(csv_path, index=False)

    metadata = {
        "source_input": str(Path(args.input)),
        "boundary_input": str(Path(args.boundaries)),
        "area_column": args.area_column,
        "parent_column": args.parent_column,
        "parent_value": args.parent_value,
        "join_predicate": "within",
        "representative_point_crs": "EPSG:32636",
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_feature_count": len(raw),
        "assigned_feature_count": int(joined[args.area_column].notna().sum()),
        "unmatched_feature_count": int(joined[args.area_column].isna().sum()),
        "output": str(output_path),
        "csv_output": str(csv_path),
        "density_columns": density_columns,
    }
    metadata_path = output_path.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {len(result)} area records to {output_path}")
    print(f"Wrote tabular indicators to {csv_path}")
    print(f"Unmatched OSM features: {metadata['unmatched_feature_count']}")


if __name__ == "__main__":
    main()