from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_version_endpoint_returns_current_version() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "v0.0.1"}
    