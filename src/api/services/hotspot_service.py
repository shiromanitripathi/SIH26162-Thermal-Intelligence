from src.models.predictor import get_predictor

MOCK_HOTSPOTS = [
    {
        "id": 1,
        "latitude": 23.7600,
        "longitude": 86.4000,
        "brightness": 345.5,
        "confidence": 0.95,
    },
    {
        "id": 2,
        "latitude": 21.1000,
        "longitude": 72.6400,
        "brightness": 332.1,
        "confidence": 0.88,
    },
]


def get_hotspots():
    return MOCK_HOTSPOTS


def get_hotspot(hotspot_id: int):
    for hotspot in MOCK_HOTSPOTS:
        if hotspot["id"] == hotspot_id:
            return hotspot
    return None


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