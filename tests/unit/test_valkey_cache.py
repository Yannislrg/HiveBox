import pytest
from unittest.mock import MagicMock, patch
from src.app.services.sensor_service import SensorService

@pytest.fixture
def sensor_service():
    """Fixture to provide a SensorService instance for testing."""
    with patch("src.app.services.sensor_service.BOX_IDS", ["box1"]):
        with patch("src.app.services.sensor_service.BASE_URL", "http://mock-api"):
            service = SensorService()
            yield service

@patch("src.app.services.sensor_service.valkey_service")
@patch("src.app.services.sensor_service.requests.get")
def test_get_data_cache_hit(mock_requests, mock_valkey, sensor_service):
    """Test that get_data returns data from Valkey cache if available."""
    mock_data = {"box1": {"data": "cached"}}
    mock_valkey.get.return_value = mock_data

    data = sensor_service.get_data()

    assert data == mock_data
    mock_valkey.get.assert_called_once_with("sensor_data")
    mock_requests.assert_not_called()

@patch("src.app.services.sensor_service.valkey_service")
@patch("src.app.services.sensor_service.requests.get")
def test_get_data_cache_miss_api_success(mock_requests, mock_valkey, sensor_service):
    """Test that get_data fetches from API and updates cache on miss."""
    mock_valkey.get.return_value = None

    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "box1", "data": "fresh"}
    mock_response.raise_for_status.return_value = None
    mock_requests.return_value = mock_response

    data = sensor_service.get_data()

    assert data == {"box1": {"id": "box1", "data": "fresh"}}
    mock_valkey.get.assert_called_once_with("sensor_data")
    mock_requests.assert_called_once()
    mock_valkey.set.assert_called_once_with("sensor_data", data)

@patch("src.app.services.sensor_service.valkey_service")
@patch("src.app.services.sensor_service.requests.get")
def test_get_data_cache_miss_api_failure_fallback(mock_requests, mock_valkey, sensor_service):
    """Test that get_data falls back to in-memory cache if API fails."""
    mock_valkey.get.return_value = None
    sensor_service.cache = {"box1": {"data": "old_in_memory"}}
    sensor_service.last_fetch_time = MagicMock()

    mock_requests.side_effect = Exception("API Down")

    with patch("src.app.services.sensor_service.datetime") as mock_datetime:
        from datetime import datetime, timezone, timedelta
        mock_datetime.now.return_value = datetime.now(timezone.utc)
        sensor_service.last_fetch_time = mock_datetime.now.return_value - timedelta(seconds=30)

        data = sensor_service.get_data()

    assert data == {"box1": {"data": "old_in_memory"}}
    mock_valkey.get.assert_called_once_with("sensor_data")

@patch("src.app.services.sensor_service.valkey_service")
def test_is_healthy_with_valkey(mock_valkey, sensor_service):
    """Test that is_healthy considers Valkey cache status."""
    # Majority unreachable (1/1 box)
    sensor_service.box_statuses = {"box1": False}

    # But cache is fresh in Valkey
    mock_valkey.is_available.return_value = True
    mock_valkey.get.return_value = {"box1": {"data": "fresh"}}

    assert sensor_service.is_healthy() is True

    mock_valkey.get.return_value = None
    sensor_service.last_fetch_time = None

    assert sensor_service.is_healthy() is False
