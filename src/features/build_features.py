"""
Lightning-fast vectorized feature engineering pipeline for FIRMS observations & OSM context.
"""

import os
import time
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import osmnx as ox
    from shapely.geometry import Point
    HAS_OSMNX = True
except ImportError:
    HAS_OSMNX = False

from src.features.feature_config import (
    RAW_FIRMS_PATH,
    PROCESSED_DATA_DIR,
    PROCESSED_FIRMS_FEATURES,
    PROCESSED_OSM_FEATURES,
    MERGED_DATASET_PATH,
    GRID_SIZE,
    OSM_RADIUS_METERS,
    WEAK_LABEL_MIN_ACTIVE_DAYS,
    WEAK_LABEL_MIN_PERSISTENCE,
    WEAK_LABEL_MIN_NIGHT_RATIO
)


def load_raw_firms(file_path: Path = RAW_FIRMS_PATH) -> pd.DataFrame:
    """Load and perform fast vector preparation on raw FIRMS CSV."""
    df = pd.read_csv(file_path)
    df["acq_date"] = pd.to_datetime(df["acq_date"])
    
    # Vectorized boolean indicators and confidence scoring
    df["is_day"] = (df["daynight"] == "D").astype(int)
    df["is_night"] = (df["daynight"] == "N").astype(int)
    df["is_type2"] = (df["type"] == 2).astype(int)
    
    conf_map = {"l": 30.0, "n": 50.0, "h": 80.0}
    if df["confidence"].dtype == object:
        df["confidence_score"] = df["confidence"].map(conf_map).fillna(50.0)
    else:
        df["confidence_score"] = df["confidence"].astype(float)
        
    return df


def aggregate_firms_spatial(df: pd.DataFrame, grid_size: float = GRID_SIZE) -> pd.DataFrame:
    """Vectorized aggregation of FIRMS observations into spatial grid cells."""
    df = df.copy()
    
    # Grid coordinates
    df["lat_grid"] = (df["latitude"] / grid_size).round() * grid_size
    df["lon_grid"] = (df["longitude"] / grid_size).round() * grid_size
    df["grid_id"] = (
        df["lat_grid"].round(4).astype(str) + "_" + df["lon_grid"].round(4).astype(str)
    )
    
    # Fast vectorized aggregation dictionary
    agg_dict = {
        "lat_grid": "first",
        "lon_grid": "first",
        "latitude": "count",
        "acq_date": ["min", "max", "nunique"],
        "is_day": "sum",
        "is_night": "sum",
        "frp": ["mean", "max", "std"],
        "brightness": ["mean", "max"],
        "bright_t31": ["mean", "max"],
        "confidence_score": "mean",
        "is_type2": "sum"
    }
    
    grouped = df.groupby("grid_id").agg(agg_dict)
    
    # Flatten MultiIndex columns
    grouped.columns = [
        "lat_grid", "lon_grid", "observation_count",
        "first_seen", "last_seen", "active_days",
        "day_observations", "night_observations",
        "mean_frp", "max_frp", "std_frp",
        "mean_brightness", "max_brightness",
        "mean_bright_t31", "max_bright_t31",
        "mean_confidence_score", "type_2_count"
    ]
    
    spatial_df = grouped.reset_index()
    
    # Compute derived vectorized thermal & temporal features
    spatial_df["std_frp"] = spatial_df["std_frp"].fillna(0.0)
    spatial_df["persistence_days"] = (
        (spatial_df["last_seen"] - spatial_df["first_seen"]).dt.days + 1
    )
    spatial_df["recurrence_ratio"] = (
        spatial_df["active_days"] / spatial_df["persistence_days"]
    )
    spatial_df["obs_per_active_day"] = (
        spatial_df["observation_count"] / spatial_df["active_days"]
    )
    spatial_df["night_ratio"] = (
        spatial_df["night_observations"] / spatial_df["observation_count"]
    )
    spatial_df["type_2_ratio"] = (
        spatial_df["type_2_count"] / spatial_df["observation_count"]
    )
    
    # Weak/heuristic multiclass target.
    # These labels are derived entirely from FIRMS behavioral features and are
    # NOT independently verified ground truth. They are intended for ML
    # benchmarking and pipeline development only.
    #
    # Historical mapping:
    # 0 = vegetation/agricultural fire
    # 1 = industrial fire candidate
    # 2 = persistent thermal source
    # 3 = other/ephemeral hotspot
    is_persistent = (
        (spatial_df["active_days"] >= 10) &
        (spatial_df["persistence_days"] >= 60) &
        (spatial_df["night_ratio"] >= 0.20)
    )

    is_industrial = (
        ~is_persistent &
        (spatial_df["active_days"] >= 4) &
        (spatial_df["night_ratio"] >= 0.25) &
        (
            (spatial_df["type_2_count"] > 0) |
            (spatial_df["mean_frp"] >= 4.0) |
            (spatial_df["active_days"] >= 7)
        )
    )

    is_vegetation = (
        ~is_persistent & ~is_industrial &
        (spatial_df["active_days"] <= 3) &
        (spatial_df["persistence_days"] <= 14) &
        (spatial_df["night_ratio"] < 0.15) &
        (spatial_df["type_2_count"] == 0)
    )

    spatial_df["target_multiclass"] = np.select(
        [is_vegetation, is_industrial, is_persistent],
        [0, 1, 2],
        default=3
    )

    # Binary persistent-source target derived consistently from the multiclass
    # weak label. This is NOT independently verified ground truth.
    spatial_df["target_persistent_source"] = np.where(
        spatial_df["target_multiclass"].isin([1, 2]),
        1,
        0
    )
    
    return spatial_df


def fetch_osm_context_single(lat: float, lon: float, radius: float = OSM_RADIUS_METERS) -> dict:
    """Deprecated legacy helper; unavailable OSM must not be represented as zero."""
    raise RuntimeError(
        "Legacy direct OSM lookup is disabled because unavailable/query-failure "
        "states were previously represented as zero-valued OSM context. "
        "Use scripts/build_osm_features.py or scripts/enrich_live_osm_context.py."
    )


def generate_fast_osm_context(spatial_df: pd.DataFrame, cache_path: Path = PROCESSED_OSM_FEATURES) -> pd.DataFrame:
    """Deprecated: synthetic OSM generation is intentionally disabled."""
    raise RuntimeError(
        "Synthetic OSM context generation is disabled. "
        "Use scripts/build_osm_features.py for real historical OSM enrichment "
        "or scripts/enrich_live_osm_context.py for the live runtime pipeline."
    )


def build_full_feature_dataset() -> pd.DataFrame:
    """Deprecated legacy pipeline retained only to fail safely."""
    raise RuntimeError(
        "The legacy full feature builder is disabled because it generated "
        "synthetic OSM values. Use the real OSM enrichment pipelines instead."
    )

if __name__ == "__main__":
    raise SystemExit(
        "Legacy synthetic feature builder is disabled. "
        "Use the provenance-aware real OSM pipelines instead."
    )
