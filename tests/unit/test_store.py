import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.app.main import app

client = TestClient(app)

@patch("src.app.routes.store.sensor_service")
@patch("src.app.routes.store.storage_service")
def test_store_endpoint_success(mock_storage, mock_sensor):
    # Setup
    mock_sensor.get_data.return_value = {"box1": {"temp": 20}}
    mock_storage.store_data.return_value = "sensor_data_20260529_120000.json"
    
    # Action
    response = client.post("/store")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Data stored successfully",
        "filename": "sensor_data_20260529_120000.json"
    }
    mock_sensor.get_data.assert_called_once()
    mock_storage.store_data.assert_called_once_with({"box1": {"temp": 20}})

@patch("src.app.routes.store.sensor_service")
def test_store_endpoint_no_data(mock_sensor):
    # Setup
    mock_sensor.get_data.return_value = {}
    
    # Action
    response = client.post("/store")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "No sensor data available to store"

@patch("src.app.routes.store.sensor_service")
@patch("src.app.routes.store.storage_service")
def test_store_endpoint_error(mock_storage, mock_sensor):
    # Setup
    mock_sensor.get_data.return_value = {"box1": {"temp": 20}}
    mock_storage.store_data.side_effect = Exception("S3 Error")
    
    # Action
    response = client.post("/store")
    
    # Assert
    assert response.status_code == 500
    assert "S3 Error" in response.json()["detail"]
