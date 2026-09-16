from fastapi import APIRouter, HTTPException, Query

from src.api.schemas.hotspot import (
    Hotspot,
    ClassificationRequest,
    ClassificationResponse,
)

from src.api.services.hotspot_service import (
    get_hotspots,
    get_hotspot,
    get_nearby_hotspots,
    classify_hotspot_cell,
)


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspots & Thermal ML Intelligence"],
)


@router.get("", response_model=list[Hotspot])
def list_hotspots():
    return get_hotspots()


@router.get("/nearby")
def nearby_hotspots(
    latitude: float,
    longitude: float,
    radius_meters: float = Query(default=2000, gt=0),
):
    return get_nearby_hotspots(
        latitude,
        longitude,
        radius_meters,
    )


@router.get("/{hotspot_id}", response_model=Hotspot)
def hotspot_detail(hotspot_id: int):
    hotspot = get_hotspot(hotspot_id)

    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot not found",
        )

    return hotspot


@router.post("/classify", response_model=ClassificationResponse)
def classify_thermal_source(request: ClassificationRequest):
    """Classify thermal source and return confidence score + human-interpretable evidence."""
    return classify_hotspot_cell(request.model_dump())


@router.get("/{hotspot_id}/classify", response_model=ClassificationResponse)
def classify_by_hotspot_id(hotspot_id: int):
    """Classify an existing hotspot ID using ML model."""
    hotspot = get_hotspot(hotspot_id)

    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot not found",
        )

    return classify_hotspot_cell(hotspot)