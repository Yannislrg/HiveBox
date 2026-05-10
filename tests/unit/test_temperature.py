"""Tests for temperature endpoint."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


@patch("src.app.routes.temperature.BOX_ID", ["test_box"])
@patch("src.app.routes.temperature.requests.get")
def test_avg_temperature_good_status(mock_get):
    """Test that temperature endpoint returns Good status for valid temperature."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
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
    mock_get.return_value = mock_response

    response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json()["average_temperature"] == 22.5
    assert response.json()["status"] == "Good"


@patch("src.app.routes.temperature.BOX_ID", ["test_box"])
@patch("src.app.routes.temperature.requests.get")
def test_avg_temperature_too_cold_status(mock_get):
    """Test that temperature endpoint returns Too Cold status for low temperature."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
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
    mock_get.return_value = mock_response

    response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json()["average_temperature"] == 5.0
    assert response.json()["status"] == "Too Cold"


@patch("src.app.routes.temperature.BOX_ID", ["test_box"])
@patch("src.app.routes.temperature.requests.get")
def test_avg_temperature_too_hot_status(mock_get):
    """Test that temperature endpoint returns Too Hot status for high temperature."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
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
    mock_get.return_value = mock_response

    response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json()["average_temperature"] == 40.0
    assert response.json()["status"] == "Too Hot"


@patch("src.app.routes.temperature.BOX_ID", ["test_box"])
@patch("src.app.routes.temperature.requests.get")
def test_avg_temperature_returns_503_when_no_valid_data(mock_get):
    """Test that the endpoint returns a non-2xx status when data is missing."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"sensors": []}
    mock_get.return_value = mock_response

    response = client.get("/temperature")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No active boxes with valid temperature data"
    }
