from fastapi import APIRouter, HTTPException

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
    try:
        result = predict(
            {
                "event_id": payload.event_id,
                "features": payload.features,
            }
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction service failed",
        ) from exc

    return PredictionResponse(**result)
