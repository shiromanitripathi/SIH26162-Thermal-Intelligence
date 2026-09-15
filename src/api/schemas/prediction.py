from typing import Any

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    event_id: str = Field(min_length=1)
    features: dict[str, Any]


class PredictionResponse(BaseModel):
    classification: str
    model_score: float | None
    evidence: list[str]
    model_version: str
    is_mock: bool