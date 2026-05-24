"""Tests for temperature endpoint."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

@pytest.fixture
def mock_sensor_service():
    with patch("src.app.routes.temperature.sensor_service") as mock:
        yield mock

def test_avg_temperature_good_status(mock_sensor_service):
    """Test that temperature endpoint returns Good status for valid temperature."""
    mock_sensor_service.get_data.return_value = {
        "test_box": {
            "sensors": [
                {
                    "title": "Temperatur",
                    "lastMeasurement": {
                        "createdAt": "2025-01-01T00:00:00.000Z",
                        "value": "22.5"
                    }
                }
            ]
        }
    }

    response = client.get("/temperature")
    assert response.status_code == 200
    assert abs(response.json()["average_temperature"] - 22.5) < 0.1
    assert response.json()["status"] == "Good"

def test_avg_temperature_too_cold_status(mock_sensor_service):
    """Test that temperature endpoint returns Too Cold status for low temperature."""
    mock_sensor_service.get_data.return_value = {
        "test_box": {
            "sensors": [
                {
                    "title": "Temperatur",
                    "lastMeasurement": {
                        "createdAt": "2025-01-01T00:00:00.000Z",
                        "value": "5.0"
                    }
                }
            ]
        }
    }

    response = client.get("/temperature")
    assert response.status_code == 200
    assert abs(response.json()["average_temperature"] - 5.0) < 0.1
    assert response.json()["status"] == "Too Cold"

def test_avg_temperature_too_hot_status(mock_sensor_service):
    """Test that temperature endpoint returns Too Hot status for high temperature."""
    mock_sensor_service.get_data.return_value = {
        "test_box": {
            "sensors": [
                {
                    "title": "Temperatur",
                    "lastMeasurement": {
                        "createdAt": "2025-01-01T00:00:00.000Z",
                        "value": "40.0"
                    }
                }
            ]
        }
    }

    response = client.get("/temperature")
    assert response.status_code == 200
    assert abs(response.json()["average_temperature"] - 40.0) < 0.1
    assert response.json()["status"] == "Too Hot"

def test_avg_temperature_returns_503_when_no_valid_data(mock_sensor_service):
    """Test that the endpoint returns a non-2xx status when data is missing."""
    mock_sensor_service.get_data.return_value = {
        "test_box": {"sensors": []}
    }

    response = client.get("/temperature")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No active boxes with valid temperature data"
    }
