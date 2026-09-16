# FIRMS Data Analysis Report

## Overview

NASA FIRMS VIIRS 375m S-NPP standard archive data was analyzed to assess
data quality, temporal behavior, spatial distribution, recurrence, and
ML-readiness for the SIH26162 Thermal Intelligence system.

## Dataset

- 1,739,550 observations
- 15 original fields
- 2023-09-15 to 2026-06-30
- VIIRS 375m S-NPP
- 960 unique acquisition dates

## Data Quality

The dataset contains:

- 0 missing cells
- 0 exact duplicate rows
- 0 invalid latitude values
- 0 invalid longitude values
- 0 invalid acquisition times

The raw FIRMS dataset was preserved without modification.

## Spatial Findings

Using a 0.01-degree exploratory spatial grid:

- 644,546 unique grid cells were identified.
- 510 grid cells contained at least 100 observations.
- 45 grid cells contained at least 1,000 observations.

This indicates substantial spatial concentration and recurrence in a smaller
subset of locations.

## Recurrence Findings

The 50 highest-observation spatial grids were examined for temporal recurrence.
These locations showed activity across hundreds of days over approximately
1,000-day spans.

This supports investigating persistence and recurrence as intelligence
features.

However, recurrent thermal activity does not by itself establish that a
location is an industrial fire.

## Label Limitations

FIRMS type values should not be treated as validated industrial-fire labels.

Type 2 was dominant in the analyzed recurrent grids (~98.32%), so it may be
considered a weak proxy for persistent/static thermal-source analysis.

Independent validation is required before making strong industrial-fire
classification claims.

## ML Handoff

The dataset provides thermal, temporal, spatial, confidence, day/night and
FIRMS type information suitable for feature development.

Potential leakage must be considered because repeated observations may belong
to the same physical source. Spatial, temporal, or grouped validation should
therefore be considered instead of relying only on random row-level splitting.

## Output

Processed dataset generated at:

`data/processed/firms_clean.csv`

Notebook:

`notebooks/firms_data_exploration.ipynb`