"""Tests for temperature endpoint."""

from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_avg_temperature():
    """Test that temperature endpoint returns 200 status code."""
    response = client.get("/temperature")
    assert response.status_code == 200
