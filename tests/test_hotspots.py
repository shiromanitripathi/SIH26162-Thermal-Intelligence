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
            "latitude": 31.224,
            "longitude": 75.770,
            "brightness": 345.5,
            "confidence": 0.95,
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
        response = client.get("/api/hotspots/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Hotspot not found"


def test_invalid_hotspot_id():
    response = client.get("/api/hotspots/abc")

    assert response.status_code == 422


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

        data = response.json()

        assert isinstance(data, list)


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
