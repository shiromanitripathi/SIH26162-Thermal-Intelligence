from fastapi import APIRouter

from src.api.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from src.models.predictor import predict


router = APIRouter(
    prefix="/api",
    tags=["Prediction"],
)


@router.post("/predict", response_model=PredictionResponse)
def predict_event(payload: PredictionRequest) -> PredictionResponse:
    result = predict(
        {
            "event_id": payload.event_id,
            "features": payload.features,
        }
    )

    return PredictionResponse(**result)