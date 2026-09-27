"""Validated geospatial transformations shared by the project workflows."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def aggregate_points_by_area(
    points_csv: str | Path,
    boundaries_path: str | Path,
    longitude_column: str = "lon",
    latitude_column: str = "lat",
    area_column: str = "ADM2_EN",
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Assign point records to areas and return area counts and point geometry.

    The input coordinates are expected to be decimal degrees in WGS84. Invalid
    or out-of-range coordinates are rejected before the spatial join so that a
    malformed upload cannot silently affect an index.
    """
    points = pd.read_csv(points_csv)
    boundaries = gpd.read_file(boundaries_path)

    required = {longitude_column, latitude_column}
    missing = sorted(required - set(points.columns))
    if missing:
        raise KeyError(f"Missing coordinate columns: {', '.join(missing)}")
    if area_column not in boundaries.columns:
        raise KeyError(f"Missing area column: {area_column}")

    longitude = pd.to_numeric(points[longitude_column], errors="coerce")
    latitude = pd.to_numeric(points[latitude_column], errors="coerce")
    invalid = (
        longitude.isna()
        | latitude.isna()
        | ~longitude.between(-180, 180)
        | ~latitude.between(-90, 90)
    )
    if invalid.any():
        raise ValueError(f"Found {int(invalid.sum())} invalid coordinate record(s)")

    points_gdf = gpd.GeoDataFrame(
        points.copy(),
        geometry=[Point(x, y) for x, y in zip(longitude, latitude)],
        crs="EPSG:4326",
    )
    if boundaries.crs is None:
        boundaries = boundaries.set_crs("EPSG:4326")
    else:
        boundaries = boundaries.to_crs("EPSG:4326")

    joined = gpd.sjoin(
        points_gdf,
        boundaries[[area_column, "geometry"]],
        how="left",
        predicate="within",
    )
    counts = joined[area_column].value_counts(dropna=True).rename("count")
    area_counts = boundaries[[area_column, "geometry"]].copy()
    area_counts["count"] = area_counts[area_column].map(counts).fillna(0).astype(int)
    points_gdf["assigned_area"] = joined[area_column].to_numpy()
    return area_counts, points_gdf