from src.models.predictor import get_predictor
from src.api.repositories.hotspot_repository import (
    get_all_hotspots,
    get_hotspot_by_id,
    get_hotspots_nearby,
)

def get_hotspots():
    return get_all_hotspots()

def get_hotspot(hotspot_id: int):
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




def classify_hotspot_cell(input_params: dict) -> dict:
    """Predict thermal source classification & explanation for a hotspot coordinate."""
    predictor = get_predictor()
    
    # Calculate grid ID
    grid_size = 0.01
    lat = float(input_params.get("latitude", 0.0))
    lon = float(input_params.get("longitude", 0.0))
    
    lat_grid = round(round(lat / grid_size) * grid_size, 4)
    lon_grid = round(round(lon / grid_size) * grid_size, 4)
    grid_id = f"{lat_grid}_{lon_grid}"
    
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
        "max_frp": input_params.get("max_frp", 12.0)
    }
    
    return predictor.predict(features)