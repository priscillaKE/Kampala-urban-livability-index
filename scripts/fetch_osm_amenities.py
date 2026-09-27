"""Fetch Kampala amenity features from OpenStreetMap with provenance metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import osmnx as ox


def build_tags(amenities: str, leisure: str) -> dict[str, list[str] | str]:
    """Build an OSMnx tag query from comma-separated CLI values."""
    tags: dict[str, list[str] | str] = {}
    amenity_values = [value.strip() for value in amenities.split(",") if value.strip()]
    leisure_values = [value.strip() for value in leisure.split(",") if value.strip()]
    if amenity_values:
        tags["amenity"] = amenity_values
    if leisure_values:
        tags["leisure"] = leisure_values
    if not tags:
        raise ValueError("At least one OSM tag value is required")
    return tags


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--place", default="Kampala, Uganda")
    parser.add_argument("--amenities", default="school,hospital")
    parser.add_argument("--leisure", default="park")
    parser.add_argument("--output", default="data/raw/osm/kampala_amenities.geojson")
    args = parser.parse_args()

    tags = build_tags(args.amenities, args.leisure)
    ox.settings.use_cache = True
    ox.settings.requests_timeout = 180

    features = ox.features_from_place(args.place, tags=tags).reset_index()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_file(output_path, driver="GeoJSON")

    metadata = {
        "source": "OpenStreetMap contributors",
        "source_url": "https://www.openstreetmap.org/",
        "license": "Open Data Commons Open Database License (ODbL)",
        "attribution": "© OpenStreetMap contributors",
        "place_query": args.place,
        "osm_tags": tags,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_count": len(features),
        "output": str(output_path),
    }
    metadata_path = output_path.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {len(features)} OSM features to {output_path}")
    print(f"Wrote provenance metadata to {metadata_path}")


if __name__ == "__main__":
    main()