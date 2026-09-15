from pydantic import BaseModel
from typing import Dict, Any, Optional


class Hotspot(BaseModel):
    id: int
    latitude: float
    longitude: float
    brightness: float
    confidence: float


class ClassificationRequest(BaseModel):
    latitude: float
    longitude: float
    observation_count: Optional[int] = 1
    active_days: Optional[int] = 1
    persistence_days: Optional[int] = 1
    night_ratio: Optional[float] = 0.0
    mean_frp: Optional[float] = 0.0
    max_frp: Optional[float] = 0.0


class ClassificationResponse(BaseModel):
    grid_id: str
    predicted_class: int
    confidence_score: float
    classification_label: str
    evidence: Dict[str, Any]
    explanation_summary: str