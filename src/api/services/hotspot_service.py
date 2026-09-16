import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.features.feature_config import PROJECT_ROOT, MERGED_DATASET_PATH
from src.models.predictor import get_predictor
from src.api.repositories.hotspot_repository import (
    get_all_hotspots,
    get_hotspot_by_id,
    get_hotspots_nearby,
)

_spatial_cache = None

def get_spatial_dataset() -> pd.DataFrame:
    """Load and cache processed thermal spatial grid cell dataset."""
    global _spatial_cache
    if _spatial_cache is None:
        if MERGED_DATASET_PATH.exists():
            _spatial_cache = pd.read_csv(MERGED_DATASET_PATH)
        else:
            # Fallback mock dataset if file not present
            _spatial_cache = pd.DataFrame([
                {
                    "grid_id": "23.76_86.40", "lat_grid": 23.76, "lon_grid": 86.40,
                    "observation_count": 3812, "active_days": 126, "persistence_days": 913,
                    "night_ratio": 0.77, "mean_frp": 3.08, "max_frp": 12.5,
                    "osm_industrial_count": 14, "osm_power_count": 4, "osm_manmade_count": 8,
                    "osm_min_distance_m": 120.5, "target_persistent_source": 1
                },
                {
                    "grid_id": "21.10_72.64", "lat_grid": 21.10, "lon_grid": 72.64,
                    "observation_count": 1955, "active_days": 163, "persistence_days": 991,
                    "night_ratio": 0.63, "mean_frp": 5.82, "max_frp": 25.0,
                    "osm_industrial_count": 18, "osm_power_count": 5, "osm_manmade_count": 12,
                    "osm_min_distance_m": 85.0, "target_persistent_source": 1
                },
                {
                    "grid_id": "30.12_74.85", "lat_grid": 30.12, "lon_grid": 74.85,
                    "observation_count": 4, "active_days": 2, "persistence_days": 3,
                    "night_ratio": 0.05, "mean_frp": 18.5, "max_frp": 32.0,
                    "osm_industrial_count": 0, "osm_power_count": 0, "osm_manmade_count": 0,
                    "osm_min_distance_m": 2000.0, "target_persistent_source": 0
                }
            ])
    return _spatial_cache


def get_hotspots(
    min_active_days: int = 1,
    persistent_only: bool = False,
    limit: int = 1500
) -> List[Dict[str, Any]]:
    """Fetch thermal spatial hotspots across India with optional filters."""
    df = get_spatial_dataset()
    
    filtered = df.copy()
    if min_active_days > 1:
        filtered = filtered[filtered["active_days"] >= min_active_days]
    if persistent_only:
        filtered = filtered[filtered["target_persistent_source"] == 1]
        
    # Prioritize active persistent candidate cells
    sorted_df = filtered.sort_values(
        ["target_persistent_source", "active_days", "observation_count"],
        ascending=[False, False, False]
    ).head(limit)
    
    results = []
    for idx, row in sorted_df.iterrows():
        results.append({
            "id": str(row["grid_id"]),
            "grid_id": str(row["grid_id"]),
            "latitude": float(row["lat_grid"]),
            "longitude": float(row["lon_grid"]),
            "brightness": float(row.get("mean_brightness", 320.0)),
            "confidence": float(row.get("mean_confidence_score", 80.0)) / 100.0,
            "observation_count": int(row["observation_count"]),
            "active_days": int(row["active_days"]),
            "persistence_days": int(row["persistence_days"]),
            "night_ratio": round(float(row["night_ratio"]), 4),
            "mean_frp": round(float(row["mean_frp"]), 2),
            "max_frp": round(float(row.get("max_frp", 0.0)), 2),
            "osm_industrial_count": int(row.get("osm_industrial_count", 0)),
            "osm_min_distance_m": round(float(row.get("osm_min_distance_m", 2000.0)), 2),
            "is_persistent": int(row.get("target_persistent_source", 0)) == 1
        })
        
    return results


def get_hotspot(hotspot_id: str) -> Optional[Dict[str, Any]]:
    """Get single spatial thermal hotspot detail by grid ID."""
    df = get_spatial_dataset()
    matches = df[df["grid_id"].astype(str) == str(hotspot_id)]
    if matches.empty:
        return None
        
    row = matches.iloc[0]
    return {
        "id": str(row["grid_id"]),
        "grid_id": str(row["grid_id"]),
        "latitude": float(row["lat_grid"]),
        "longitude": float(row["lon_grid"]),
        "brightness": float(row.get("mean_brightness", 320.0)),
        "confidence": float(row.get("mean_confidence_score", 80.0)) / 100.0,
        "observation_count": int(row["observation_count"]),
        "active_days": int(row["active_days"]),
        "persistence_days": int(row["persistence_days"]),
        "night_ratio": round(float(row["night_ratio"]), 4),
        "mean_frp": round(float(row["mean_frp"]), 2),
        "max_frp": round(float(row.get("max_frp", 0.0)), 2),
        "osm_industrial_count": int(row.get("osm_industrial_count", 0)),
        "osm_min_distance_m": round(float(row.get("osm_min_distance_m", 2000.0)), 2),
        "is_persistent": int(row.get("target_persistent_source", 0)) == 1
    }


def classify_hotspot_cell(input_params: dict) -> dict:
    """Predict thermal source classification & explanation using trained ML model."""
    predictor = get_predictor()
    
    grid_size = 0.01
    lat = float(input_params.get("latitude", 0.0))
    lon = float(input_params.get("longitude", 0.0))
    
    lat_grid = round(round(lat / grid_size) * grid_size, 4)
    lon_grid = round(round(lon / grid_size) * grid_size, 4)
    grid_id = input_params.get("grid_id", f"{lat_grid}_{lon_grid}")
    
    features = {
        "grid_id": grid_id,
        "lat_grid": lat_grid,
        "lon_grid": lon_grid,
        "observation_count": input_params.get("observation_count", 10),
        "active_days": input_params.get("active_days", 5),
        "persistence_days": input_params.get("persistence_days", 30),
        "recurrence_ratio": input_params.get("active_days", 5) / max(1, input_params.get("persistence_days", 30)),
        "night_ratio": input_params.get("night_ratio", 0.5),
        "mean_frp": input_params.get("mean_frp", 5.0),
        "max_frp": input_params.get("max_frp", 12.0),
        "osm_industrial_count": input_params.get("osm_industrial_count", 0),
        "osm_min_distance_m": input_params.get("osm_min_distance_m", 2000.0)
    }
    
    return predictor.predict(features)


def get_hotspot_stats() -> Dict[str, Any]:
    """Get system-wide summary statistics."""
    df = get_spatial_dataset()
    return {
        "total_raw_observations": 1739550,
        "total_spatial_cells": len(df),
        "persistent_candidate_cells": int((df["target_persistent_source"] == 1).sum()),
        "ephemeral_fire_cells": int((df["target_persistent_source"] == 0).sum()),
        "max_active_days": int(df["active_days"].max()),
        "max_persistence_days": int(df["persistence_days"].max()),
        "mean_night_ratio": round(float(df["night_ratio"].mean()), 4)
    }