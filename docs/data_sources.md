# Data Sources

## OpenStreetMap

The acquisition script `scripts/fetch_osm_amenities.py` retrieves mapped amenities for Kampala using OSMnx and the OpenStreetMap Overpass service.

Example:

```bash
python scripts/fetch_osm_amenities.py \
  --place "Kampala, Uganda" \
  --amenities school,hospital \
  --leisure park \
  --output data/raw/osm/kampala_amenities.geojson
```

For parish-level Kampala outputs, process against ADM4 using the unique code key and filter the parent district:

```bash
python scripts/process_osm_amenities.py \
  --input data/raw/osm/kampala_amenities.geojson \
  --boundaries data/boundaries/uga_admbnda_adm4_ubos_20200824.shp \
  --area-column ADM4_PCODE \
  --parent-column ADM2_EN \
  --parent-value Kampala \
  --output data/processed/osm/kampala_parish_osm_indicators.geojson
```

The script writes a sidecar metadata file containing the query, retrieval time, source, license, attribution, and feature count. Raw downloads should not be edited manually. Processed indicator tables should retain a reference to the corresponding metadata file.

The processing step also writes a CSV with area size and amenity densities. Density is calculated per square kilometre using EPSG:32636 for area measurement. It is a geographic exposure measure, not a population-adjusted service-access measure; population data is still required for that interpretation.

OpenStreetMap data is provided under the Open Data Commons Open Database License. Display and redistribution must preserve the required attribution and comply with the current ODbL terms.

OSM coverage is uneven and reflects mapped features, not a complete census. A low feature count may indicate missing mapping rather than low service availability. OSM-derived indicators should therefore include a data-quality note and should not be treated as a standalone measure of service provision.