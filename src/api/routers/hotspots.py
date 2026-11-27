"""REST endpoints for querying thermal hotspots and running ML classification."""

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas.hotspot import (
    ClassificationRequest,
    ClassificationResponse,
    Hotspot,
)
from src.api.services.hotspot_service import (
    classify_hotspot_cell,
    get_hotspot,
    get_hotspot_stats,
    get_hotspots,
    get_nearby_hotspots,
)


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspots & Thermal ML Intelligence"],
)


@router.get("", response_model=list[Hotspot])
def list_hotspots(
    min_active_days: int = Query(default=1, ge=1),
    persistent_only: bool = Query(default=False),
    limit: int = Query(default=1500, ge=1, le=10000),
):
    """Fetch thermal event grid cells from PostgreSQL with optional filters."""
    return get_hotspots(
        min_active_days=min_active_days,
        persistent_only=persistent_only,
        limit=limit,
    )


@router.get("/stats")
def hotspot_summary_stats():
    """Return aggregate counts (total cells, persistent/ephemeral, OSM coverage)."""
    return get_hotspot_stats()


@router.get("/nearby")
def nearby_hotspots(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_meters: float = Query(default=2000, gt=0, le=100000),
):
    """Find hotspots within radius_meters of (latitude, longitude) using PostGIS."""
    return get_nearby_hotspots(
        latitude,
        longitude,
        radius_meters,
    )


@router.post("/classify", response_model=ClassificationResponse)
def classify_thermal_source(request: ClassificationRequest):
    """Classify a hotspot from explicit feature values sent in the request body."""
    try:
        return classify_hotspot_cell(
            request.model_dump(exclude_none=True)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get(
    "/{hotspot_id}/classify",
    response_model=ClassificationResponse,
)
def classify_by_hotspot_id(hotspot_id: str):
    """Look up a hotspot in PostgreSQL by ID/grid_id and classify it with the ML model."""
    hotspot = get_hotspot(hotspot_id)

    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot not found",
        )

    try:
        return classify_hotspot_cell(hotspot)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get("/{hotspot_id}", response_model=Hotspot)
def hotspot_detail(hotspot_id: str):
    """Return full details for a single hotspot by numeric ID, event_id, or grid_id."""
    hotspot = get_hotspot(hotspot_id)

    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot not found",
        )

    return hotspot
