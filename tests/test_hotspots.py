from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_hotspots():
    response = client.get("/api/hotspots")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_get_hotspot():
    response = client.get("/api/hotspots/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


def test_hotspot_not_found():
    response = client.get("/api/hotspots/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Hotspot not found"


def test_invalid_hotspot_id():
    response = client.get("/api/hotspots/abc")

    assert response.status_code == 422