import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from src.app.main import app
from src.app.services.sensor_service import SensorService

client = TestClient(app)

@pytest.fixture
def mock_sensor_service():
    """Fixture to mock SensorService for readiness tests."""
    with patch("src.app.routes.readyz.sensor_service") as mock:
        yield mock

def test_readyz_nominal_case(mock_sensor_service):
    """Scenario 1: Nominal case (all healthy)."""
    mock_sensor_service.is_healthy.return_value = True
    response = client.get("/readyz")
    assert response.status_code == 200

def test_readyz_unhealthy_majority_unreachable_and_stale_cache(mock_sensor_service):
    """Scenario 4: Majority unreachable AND stale cache."""
    mock_sensor_service.is_healthy.return_value = False
    response = client.get("/readyz")
    assert response.status_code == 503
    assert "Service Unhealthy" in response.text

@patch("src.app.services.sensor_service.BOX_IDS", ["box1", "box2", "box3"])
def test_sensor_service_logic_nominal():
    """Scenario 1: Nominal case (all healthy)."""
    service = SensorService()
    assert service.is_healthy() is True

@patch("src.app.services.sensor_service.BOX_IDS", ["box1", "box2", "box3"])
def test_sensor_service_logic_majority_unreachable_fresh_cache():
    """Scenario 4: Majority unreachable but cache is fresh."""
    service = SensorService()

    service.box_statuses = {"box1": False, "box2": False, "box3": True}

    service.last_fetch_time = datetime.now(timezone.utc) - timedelta(minutes=1)


    assert service.is_healthy() is True

@patch("src.app.services.sensor_service.BOX_IDS", ["box1", "box2", "box3"])
def test_sensor_service_logic_majority_unreachable_stale_cache():
    """Scenario 4: Majority unreachable and cache is stale."""
    service = SensorService()

    service.box_statuses = {"box1": False, "box2": False, "box3": True}

    service.last_fetch_time = datetime.now(timezone.utc) - timedelta(minutes=6)

    assert service.is_healthy() is False

@patch("src.app.services.sensor_service.BOX_IDS", ["box1", "box2", "box3"])
def test_sensor_service_logic_minority_unreachable_stale_cache():
    """Scenario 5: Minority unreachable but cache is stale."""
    service = SensorService()

    service.box_statuses = {"box1": False, "box2": True, "box3": True}

    service.last_fetch_time = datetime.now(timezone.utc) - timedelta(minutes=6)

    assert service.is_healthy() is True
