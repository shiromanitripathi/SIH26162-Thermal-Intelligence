from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Hotspot(BaseModel):
    id: int | str
    event_id: str | None = None
    grid_id: str | None = None
    latitude: float
    longitude: float

    observation_count: int | None = None
    active_days: int | None = None
    first_seen: date | None = None
    last_seen: date | None = None
    persistence_days: int | None = None
    recurrence_ratio: float | None = None
    obs_per_active_day: float | None = None
    day_observations: int | None = None
    night_observations: int | None = None
    night_ratio: float | None = None

    mean_frp: float | None = None
    max_frp: float | None = None
    std_frp: float | None = None
    mean_brightness: float | None = None
    brightness: float | None = None
    max_brightness: float | None = None
    mean_bright_t31: float | None = None
    max_bright_t31: float | None = None

    mean_confidence_score: float | None = None
    confidence: float | None = None
    type_2_count: int | None = None
    type_2_ratio: float | None = None

    target_persistent_source: int | None = None
    target_multiclass: int | None = None

    osm_context_available: bool | None = None
    osm_feature_count: int | None = None
    osm_industrial_count: int | None = None
    osm_power_count: int | None = None
    osm_manmade_count: int | None = None
    osm_min_distance_m: float | None = None


class ClassificationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    grid_id: str | None = None
    event_id: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    features: dict[str, Any] | None = None

    observation_count: int | None = Field(default=None, ge=0)
    active_days: int | None = Field(default=None, ge=0)
    persistence_days: int | None = Field(default=None, ge=0)
    night_ratio: float | None = Field(default=None, ge=0, le=1)
    mean_frp: float | None = Field(default=None, ge=0)
    max_frp: float | None = Field(default=None, ge=0)


class ClassificationResponse(BaseModel):
    grid_id: str | None = None
    classification: str
    predicted_class: int | str | None = None
    confidence_score: float | None = None
    model_score: float | None = None
    classification_label: str | None = None
    evidence: list[str]
    explanation_summary: str | None = None
    model_version: str
    is_mock: bool