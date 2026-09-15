from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from src.api.schemas.hotspot import Hotspot, ClassificationRequest, ClassificationResponse
from src.api.services.hotspot_service import (
    get_hotspots,
    get_hotspot,
    classify_hotspot_cell,
    get_hotspot_stats
)


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspots & Thermal ML Intelligence"],
)


@router.get("", response_model=List[Dict[str, Any]])
def list_hotspots(
    min_active_days: int = Query(default=1, ge=1, description="Minimum active days filter"),
    persistent_only: bool = Query(default=False, description="Filter persistent thermal candidates only"),
    limit: int = Query(default=1500, ge=1, le=10000, description="Max points limit")
):
    """List spatial thermal grid hotspots across India with live parameter filtering."""
    return get_hotspots(min_active_days=min_active_days, persistent_only=persistent_only, limit=limit)


@router.get("/stats")
def hotspot_summary_stats():
    """Get system-wide summary statistics of FIRMS observations, grid cells, and persistent candidates."""
    return get_hotspot_stats()


@router.get("/{hotspot_id}")
def hotspot_detail(hotspot_id: str):
    hotspot = get_hotspot(hotspot_id)
    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot grid cell not found",
        )
    return hotspot


@router.post("/classify", response_model=ClassificationResponse)
def classify_thermal_source(request: ClassificationRequest):
    """Classify thermal source and return confidence score + human-interpretable evidence."""
    return classify_hotspot_cell(request.model_dump())


@router.get("/{hotspot_id}/classify", response_model=ClassificationResponse)
def classify_by_hotspot_id(hotspot_id: str):
    """Classify an existing hotspot ID using ML model."""
    hotspot = get_hotspot(hotspot_id)
    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot grid cell not found",
        )
    return classify_hotspot_cell(hotspot)