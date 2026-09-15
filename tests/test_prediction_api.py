from fastapi.testclient import TestClient
from src.api.routers import prediction as prediction_router

from src.api.main import app


client = TestClient(app)


def test_predict_mock_success():
    response = client.post(
        "/api/predict",
        json={
            "event_id": "EVT_TEST_001",
            "features": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["classification"] == "MODEL_NOT_AVAILABLE"
    assert data["model_score"] is None
    assert data["is_mock"] is True
    assert data["model_version"] == "mock-v0"
    assert isinstance(data["evidence"], list)


def test_predict_missing_event_id():
    response = client.post(
        "/api/predict",
        json={
            "features": {},
        },
    )

    assert response.status_code == 422


def test_predict_invalid_features():
    response = client.post(
        "/api/predict",
        json={
            "event_id": "EVT_TEST_001",
            "features": "invalid",
        },
    )

    assert response.status_code == 422

def test_predictor_failure_returns_clean_500(monkeypatch):
    def failing_predict(_input_data):
        raise RuntimeError("simulated predictor failure")

    monkeypatch.setattr(
        prediction_router,
        "predict",
        failing_predict,
    )

    response = client.post(
        "/api/predict",
        json={
            "event_id": "EVT_TEST_FAILURE",
            "features": {},
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Prediction service failed"
    }