# Kampala Urban Livability and Opportunity Index

An open, reproducible geospatial project for comparing livability across Kampala's administrative areas. The project is designed to combine affordability, access to opportunity, essential services, environmental quality, and safety into an explainable composite index.

## Current Status

The repository currently includes:

- Boundary exploration and area calculations
- Point-data ingestion and spatial joins
- Static and interactive map generation
- A reusable composite-index engine in `src/index.py`
- Tests covering normalization, weights, ranking, and missing data

The full multi-source index is still under development. Current school-point outputs are demonstration data and should not be interpreted as a complete livability ranking.

## Data Sources

See [docs/data_sources.md](docs/data_sources.md) for the first reproducible external-data workflow. OpenStreetMap features are treated as mapped observations, not a complete inventory of Kampala services.

Population-adjusted indicators follow the input contract in [docs/population_data.md](docs/population_data.md). A documented population source is required before producing per-resident service rates.

## Project Structure

```text
kampala-urban-livability-index/
├── data/                  # Boundaries, samples, and processed outputs
├── dashboard/             # Streamlit application
├── docs/                  # Methodology and data documentation
├── scripts/               # Command-line processing and visualization scripts
├── src/                   # Reusable analysis modules
├── tests/                 # Automated tests
├── explore_shapefiles.ipynb
├── requirements.txt
└── LICENSE
```

## Getting Started

```bash
git clone https://github.com/priscillaKE/Kampala-urban-livability-index.git
cd Kampala-urban-livability-index
python -m venv .venv
```

Activate the environment using the command appropriate for your operating system, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Calculate a ranked index from an area-level CSV:

```bash
python scripts/calculate_index.py \
	--input data/samples/demo_area_indicators.csv \
	--output outputs/demo_index.csv \
	--indicators service_access,green_space,monthly_rent \
	--lower-is-better monthly_rent \
	--weights service_access=2,green_space=1,monthly_rent=2
```

The checked-in indicator file is illustrative test data, not an official Kampala dataset. Replace it with documented observations before drawing conclusions.

## Methodology

The planned index is a weighted combination of normalized indicators. Each indicator documents whether a higher or lower value is better, its source, collection date, geographic level, and known limitations.

```text
livability_score = 100 * sum(weight * normalized_indicator) / sum(available_weights)
```

Scores include a `data_completeness` field so areas with sparse data are not presented with false precision. See [docs/methodology.md](docs/methodology.md) for the scoring rules and planned indicator groups.

## Data Principles

Every dataset added to the project should record its source, date, geographic level, license, processing steps, and limitations. Raw data should remain separate from processed outputs, and conclusions should distinguish observed data from assumptions.

## Planned Development

1. Add documented affordability, opportunity, service-access, environment, and safety indicators.
2. Normalize counts by population or area where appropriate.
3. Add sensitivity analysis and uncertainty-aware rankings.
4. Connect the composite index to the dashboard with score explanations.
5. Add historical snapshots to measure neighbourhood change over time.

## License

MIT License. Individual datasets may have additional terms; consult their source documentation before redistribution.
