from fastapi import APIRouter, HTTPException

from src.api.schemas.hotspot import Hotspot
from src.api.services.hotspot_service import (
    get_hotspots,
    get_hotspot,
)


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspots"],
)


@router.get("", response_model=list[Hotspot])
def list_hotspots():
    return get_hotspots()

@router.get("/{hotspot_id}", response_model=Hotspot)
def hotspot_detail(hotspot_id: int):
    hotspot = get_hotspot(hotspot_id)

    if hotspot is None:
        raise HTTPException(
            status_code=404,
            detail="Hotspot not found",
        )

    return hotspot