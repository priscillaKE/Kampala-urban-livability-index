# Methodology

## Purpose

The Kampala Urban Livability and Opportunity Index is intended to support comparison and exploration, not to produce an absolute or permanent definition of the best place to live. A score is only as credible as the data, geographic unit, and assumptions behind it.

## Geographic Unit

Indicators are joined to a common administrative geography before scoring. The boundary source, release date, coordinate reference system, and any simplification must be recorded with the output.

## Indicator Design

Each indicator should have:

- A clear definition and unit
- A source URL or publication reference
- A collection or publication date
- A geographic level
- A direction: higher-is-better or lower-is-better
- A reason for inclusion
- A known limitation

Recommended indicator groups are affordability, economic opportunity, essential services, mobility, environment, safety, and infrastructure.

## Normalization

The current implementation uses min-max normalization:

```text
normalized = (value - minimum) / (maximum - minimum)
```

For indicators where lower values are better, the normalized value is reversed. Missing values remain missing rather than being silently treated as zero. Constant indicators receive 0.5 for observed rows because they do not differentiate areas.

For future datasets with extreme outliers, a documented percentile or robust normalization method may be preferable. The method must be applied consistently and recorded in the output metadata.

## Composite Score

For area i and indicator j:

```text
score_i = 100 * sum(w_j * x_ij) / sum(w_j for available indicators)
```

Weights must be non-negative and their interpretation must be documented. The denominator uses only available indicators, while `data_completeness` reports the proportion of requested indicators present for that area.

## Interpretation

Scores are relative to the areas and data included in a run. A score of 80 does not mean that an area satisfies 80 percent of an external standard. Rankings should be published with indicator values, completeness, data dates, and sensitivity results.

## Sensitivity Analysis

Rankings should be recomputed under several documented weight scenarios, such as balanced, affordability-priority, or service-access-priority. `src/sensitivity.py` returns each scenario separately and summarizes each area's minimum, maximum, and mean rank. A large rank range means the conclusion depends strongly on the chosen priorities and should be reported as uncertain.

## Required Quality Checks

Before publishing a ranking:

1. Validate coordinate ranges and geometry validity.
2. Report records that could not be assigned to an area.
3. Check duplicates and missing values.
4. Prefer population-adjusted or area-adjusted measures for raw counts.
5. Compare rankings under reasonable alternative weights.
6. Record all source and processing metadata.

## Limitations

The current repository contains boundary processing and sample school-point data, not a complete citywide index. Until multiple documented data sources are integrated, outputs should be treated as technical demonstrations rather than policy recommendations.
