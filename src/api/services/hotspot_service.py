from __future__ import annotations

from typing import Any

from src.api.repositories.hotspot_repository import (
    get_all_hotspots,
    get_hotspot_by_id,
    get_hotspot_stats as get_hotspot_stats_from_db,
    get_hotspots_nearby,
)
from src.models.predictor import get_predictor


def get_hotspots(
    min_active_days: int = 1,
    persistent_only: bool = False,
    limit: int = 1500,
) -> list[dict]:
    return get_all_hotspots(
        min_active_days=min_active_days,
        persistent_only=persistent_only,
        limit=limit,
    )


def get_hotspot(hotspot_id: str | int) -> dict | None:
    return get_hotspot_by_id(hotspot_id)


def get_nearby_hotspots(
    latitude: float,
    longitude: float,
    radius_meters: float = 2000,
) -> list[dict]:
    return get_hotspots_nearby(
        latitude,
        longitude,
        radius_meters,
    )


def get_hotspot_stats() -> dict:
    return get_hotspot_stats_from_db()


def classify_hotspot_cell(input_params: dict[str, Any]) -> dict[str, Any]:
    """
    Classify one event/grid cell without inventing missing model features.

    A real loaded model must receive every feature recorded in its artifact
    contract. If a feature is missing, the predictor raises ValueError and the
    API returns HTTP 422. When no artifact is installed, the predictor returns
    an explicit MODEL_NOT_AVAILABLE response.
    """
    predictor = get_predictor()

    payload = dict(input_params)
    nested_features = payload.pop("features", None)

    if isinstance(nested_features, dict):
        features = dict(nested_features)
        for key, value in payload.items():
            if value is not None and key not in features:
                features[key] = value
    else:
        features = {
            key: value
            for key, value in payload.items()
            if value is not None
        }

    latitude = features.get("latitude")
    longitude = features.get("longitude")

    if latitude is not None and longitude is not None:
        grid_size = 0.01
        lat_grid = round(round(float(latitude) / grid_size) * grid_size, 4)
        lon_grid = round(round(float(longitude) / grid_size) * grid_size, 4)
        features.setdefault("lat_grid", lat_grid)
        features.setdefault("lon_grid", lon_grid)
        features.setdefault("grid_id", f"{lat_grid}_{lon_grid}")

    event_id = (
        features.get("event_id")
        or features.get("grid_id")
        or "unidentified-event"
    )

    return predictor.predict(
        {
            "event_id": str(event_id),
            "features": features,
        }
    )
