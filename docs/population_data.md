# Population Data Contract

Population adjustment is the next required input for the index. The population table must contain one row per boundary unit and use the same stable key as the processed indicator table.

Required columns:

```text
ADM4_PCODE,population
```

The acquisition source, reference year, estimate type, and license must be recorded. The project should prefer an official census or a documented gridded population product and should not mix population years with indicator observations without documenting the time mismatch.

Run the enrichment after obtaining a documented population CSV:

```bash
python scripts/add_population.py \
  --indicators data/processed/osm/kampala_parish_osm_indicators.csv \
  --population data/raw/population/kampala_adm4_population.csv \
  --output data/processed/osm/kampala_population_adjusted.csv \
  --population-source "Official source URL or publication" \
  --population-date "YYYY or YYYY-MM-DD"
```

The workflow calculates amenity counts per 10,000 residents. It rejects duplicate area keys, missing population values, and non-positive populations so a partial join cannot silently create misleading rates.