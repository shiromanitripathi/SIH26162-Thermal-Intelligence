from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

SPATIAL_DATASET = PROCESSED_DIR / "firms_spatial_features.csv"
MERGED_DATASET = PROCESSED_DIR / "firms_osm_merged_dataset.csv"

TARGET = "target_multiclass"

IDENTIFIER_COLUMNS = [
    "grid_id",
    "lat_grid",
    "lon_grid",
]

TARGET_COLUMNS = [
    "target_multiclass",
    "target_persistent_source",
]

FIRMS_FEATURES = [
    "observation_count",
    "active_days",
    "day_observations",
    "night_observations",
    "mean_frp",
    "max_frp",
    "std_frp",
    "mean_brightness",
    "max_brightness",
    "mean_bright_t31",
    "max_bright_t31",
    "mean_confidence_score",
    "type_2_count",
    "persistence_days",
    "recurrence_ratio",
    "obs_per_active_day",
    "night_ratio",
    "type_2_ratio",
]

RANDOM_STATE = 42

TEST_SIZE = 0.20
VALIDATION_SIZE = 0.20

SPATIAL_BLOCK_SIZE = 0.10
