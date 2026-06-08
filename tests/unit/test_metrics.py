"""Unit tests for Prometheus metrics endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_metrics_endpoint_exists(client):
    """Test that /metrics endpoint exists and returns 200."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_endpoint_returns_prometheus_format(client):
    """Test that /metrics endpoint returns Prometheus-formatted metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    # Check for Prometheus metric format
    assert "hivebox_requests_total" in content
    assert "hivebox_temperature_celsius" in content
    assert "hivebox_temperature_status" in content
    assert "hivebox_temperature_seconds" in content
    assert "hivebox_temperature_readings_total" in content
    assert "hivebox_temperature_endpoint_requests_total" in content
    assert "hivebox_metrics_endpoint_requests_total" in content
    assert "hivebox_healthy_boxes_total" in content
    assert "hivebox_cache_miss_total" in content


def test_metrics_endpoint_content_type(client):
    """Test that /metrics endpoint returns correct content type."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain; version=0.0.4" in response.headers.get("content-type", "")


def test_metrics_endpoint_increments_counter(client):
    """Test that metrics counter increments on each request."""
    # First request
    response1 = client.get("/metrics")
    content1 = response1.text
    metrics_endpoint_requests1 = sum(
        float(line.split(" ")[1])
        for line in content1.split("\n")
        if line.startswith("hivebox_metrics_endpoint_requests_total")
    )

    # Second request
    response2 = client.get("/metrics")
    content2 = response2.text
    metrics_endpoint_requests2 = sum(
        float(line.split(" ")[1])
        for line in content2.split("\n")
        if line.startswith("hivebox_metrics_endpoint_requests_total")
    )

    # Counter should have incremented
    assert metrics_endpoint_requests2 > metrics_endpoint_requests1


def test_metrics_endpoint_includes_all_metrics(client):
    """Test that all expected metrics are present in the output."""
    response = client.get("/metrics")
    content = response.text

    # Check for all metric types
    assert "hivebox_requests_total" in content
    assert "hivebox_temperature_celsius" in content
    assert "hivebox_temperature_status" in content
    assert "hivebox_temperature_seconds" in content
    assert "hivebox_temperature_readings_total" in content
    assert "hivebox_temperature_endpoint_requests_total" in content
    assert "hivebox_metrics_endpoint_requests_total" in content
    assert "hivebox_healthy_boxes_total" in content
    assert "hivebox_cache_miss_total" in content

    # Check for metric types
    assert "# HELP" in content
    assert "# TYPE" in content
