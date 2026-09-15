from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_openapi_includes_predict_endpoint():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/api/predict" in schema["paths"]
    assert "post" in schema["paths"]["/api/predict"]


def test_swagger_docs_load():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_cors_allows_frontend_origin():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )