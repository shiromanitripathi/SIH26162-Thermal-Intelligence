from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_hotspots():
    mock_hotspots = [
        {
            "id": 1,
            "event_id": "EVT_1",
            "grid_id": "31.22_75.77",
            "latitude": 31.224,
            "longitude": 75.770,
            "brightness": 345.5,
            "confidence": 0.95,
            "active_days": 4,
        }
    ]

    with patch(
        "src.api.routers.hotspots.get_hotspots",
        return_value=mock_hotspots,
    ):
        response = client.get("/api/hotspots")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1


def test_get_hotspot_not_found():
    with patch(
        "src.api.routers.hotspots.get_hotspot",
        return_value=None,
    ):
        response = client.get("/api/hotspots/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Hotspot not found"


def test_get_hotspot_by_grid_id():
    mock_hotspot = {
        "id": 1,
        "event_id": "EVT_1",
        "grid_id": "31.22_75.77",
        "latitude": 31.224,
        "longitude": 75.770,
        "brightness": 345.5,
        "confidence": 0.95,
    }

    with patch(
        "src.api.routers.hotspots.get_hotspot",
        return_value=mock_hotspot,
    ):
        response = client.get(
            "/api/hotspots/31.22_75.77"
        )

    assert response.status_code == 200
    assert response.json()["grid_id"] == "31.22_75.77"


def test_nearby_hotspots():
    with patch(
        "src.api.routers.hotspots.get_nearby_hotspots",
        return_value=[],
    ):
        response = client.get(
            "/api/hotspots/nearby",
            params={
                "latitude": 31.224,
                "longitude": 75.770,
                "radius_meters": 2000,
            },
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nearby_hotspots_invalid_radius():
    response = client.get(
        "/api/hotspots/nearby",
        params={
            "latitude": 31.224,
            "longitude": 75.770,
            "radius_meters": 0,
        },
    )

    assert response.status_code == 422


def test_nearby_hotspots_invalid_latitude():
    response = client.get(
        "/api/hotspots/nearby",
        params={
            "latitude": 123.0,
            "longitude": 75.770,
            "radius_meters": 2000,
        },
    )

    assert response.status_code == 422
