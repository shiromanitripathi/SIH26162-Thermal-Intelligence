# Live FIRMS Runtime Pipeline

The live runtime dataset is separate from the historical ML benchmark dataset.

## FIRMS source

The runtime ingest uses NASA FIRMS VIIRS NOAA-20 NRT and NOAA-21 NRT.
The FIRMS MAP key is loaded from .env and is not committed.

The live NRT dataset is not written to data/processed/firms_spatial_features.csv.

## OSM provenance

Only persisted successful real OSM tile results are treated as verified context.
Unqueried cells keep osm_context_available = FALSE and OSM values remain NULL.

## Runtime model

The trained final runtime model artifact is not stored in the repository.
When absent, the API returns MODEL_NOT_AVAILABLE with a null model score.
