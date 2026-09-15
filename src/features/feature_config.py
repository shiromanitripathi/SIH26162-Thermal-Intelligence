"""
Feature configuration and pipeline constants for SIH26162 Thermal Intelligence.
"""

from pathlib import Path

# File Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FIRMS_PATH = PROJECT_ROOT / "data" / "raw" / "FIRMS" / "fire_archive_SV-C2_806010.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_FIRMS_FEATURES = PROCESSED_DATA_DIR / "firms_spatial_features.csv"
PROCESSED_OSM_FEATURES = PROCESSED_DATA_DIR / "osm_context_features.csv"
MERGED_DATASET_PATH = PROCESSED_DATA_DIR / "firms_osm_merged_dataset.csv"

# Spatial Aggregation Parameters
GRID_SIZE = 0.01  # approximately 1 km at the equator

# Candidate Filtering Criteria for OSM Context Extraction
# Filters cells with meaningful thermal activity to optimize OSM API queries
OSM_CANDIDATE_MIN_OBS = 3
OSM_CANDIDATE_MIN_ACTIVE_DAYS = 2

# OSM Query Tags & Distance Radius
OSM_RADIUS_METERS = 2000
OSM_TAGS = {
    "landuse": ["industrial", "construction", "commercial", "quarry"],
    "industrial": True,
    "power": True,
    "man_made": ["works", "storage_tank", "chimney", "petroleum_refinery", "pipeline"],
    "amenity": ["waste_transfer", "waste_disposal"]
}

# FIRMS Thermal & Temporal Feature Columns
FIRMS_FEATURE_COLS = [
    "observation_count",
    "active_days",
    "persistence_days",
    "recurrence_ratio",
    "obs_per_active_day",
    "day_observations",
    "night_observations",
    "night_ratio",
    "mean_frp",
    "max_frp",
    "std_frp",
    "mean_brightness",
    "max_brightness",
    "mean_bright_t31",
    "max_bright_t31",
    "mean_confidence_score",
    "type_2_count",
    "type_2_ratio"
]

# OSM Context Feature Columns
OSM_FEATURE_COLS = [
    "osm_feature_count",
    "osm_industrial_count",
    "osm_power_count",
    "osm_manmade_count",
    "osm_min_distance_m"
]

# Combined Model Feature List
ALL_MODEL_FEATURES = FIRMS_FEATURE_COLS + OSM_FEATURE_COLS

# Weak Supervision Label Definition Constants
# Target Y = 1: Persistent Static Thermal Source / Industrial Candidate
# Defined strictly using FIRMS temporal & thermal properties (Zero OSM Leakage)
WEAK_LABEL_MIN_ACTIVE_DAYS = 5
WEAK_LABEL_MIN_PERSISTENCE = 30
WEAK_LABEL_MIN_NIGHT_RATIO = 0.30
