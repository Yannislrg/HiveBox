"""Integration tests for HiveBox API endpoints.

These tests run against the Docker container to verify end-to-end functionality.
"""

import pytest
import requests
from requests.exceptions import HTTPError


@pytest.fixture(scope="module")
def client():
    """Base URL for the API endpoint.
    
    Returns:
        str: The base URL where the API is running.
    """
    return "http://localhost:8000"


@pytest.fixture(scope="module")
def version_response(client):
    """Get the version endpoint response.
    
    Args:
        client: The base URL for the API.
    
    Returns:
        requests.Response: The response from the /version endpoint.
    """
    return requests.get(f"{client}/version")


@pytest.fixture(scope="module")
def temperature_response(client):
    """Get the temperature endpoint response.
    
    Args:
        client: The base URL for the API.
    
    Returns:
        requests.Response: The response from the /temperature endpoint.
    """
    return requests.get(f"{client}/temperature")


@pytest.fixture(scope="module")
def metrics_response(client):
    """Get the metrics endpoint response.
    
    Args:
        client: The base URL for the API.
    
    Returns:
        requests.Response: The response from the /metrics endpoint.
    """
    return requests.get(f"{client}/metrics")


class TestVersionEndpoint:
    """Test suite for the /version endpoint."""

    def test_version_endpoint_returns_200(self, version_response):
        """Test that /version returns HTTP 200 OK.
        
        Args:
            version_response: The response from the /version endpoint.
        
        Asserts:
            The response status code is 200.
        """
        assert version_response.status_code == 200

    def test_version_endpoint_returns_json(self, version_response):
        """Test that /version returns JSON content.
        
        Args:
            version_response: The response from the /version endpoint.
        
        Asserts:
            The response content type is JSON.
        """
        assert version_response.headers["Content-Type"] == "application/json"

    def test_version_endpoint_returns_version_field(self, version_response):
        """Test that /version returns a 'version' field.
        
        Args:
            version_response: The response from the /version endpoint.
        
        Asserts:
            The response contains a 'version' key.
        """
        assert "version" in version_response.json()

    def test_version_endpoint_returns_expected_version(self, version_response):
        """Test that /version returns the expected version string.
        
        Args:
            version_response: The response from the /version endpoint.
        
        Asserts:
            The version is 'v0.0.2'.
        """
        assert version_response.json()["version"] == "v0.0.2"


class TestTemperatureEndpoint:
    """Test suite for the /temperature endpoint."""

    def test_temperature_endpoint_returns_200(self, temperature_response):
        """Test that /temperature returns HTTP 200 OK.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The response status code is 200.
        """
        assert temperature_response.status_code == 200

    def test_temperature_endpoint_returns_json(self, temperature_response):
        """Test that /temperature returns JSON content.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The response content type is JSON.
        """
        assert temperature_response.headers["Content-Type"] == "application/json"

    def test_temperature_endpoint_returns_expected_fields(self, temperature_response):
        """Test that /temperature returns expected response fields.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The response contains 'average_temperature' and 'status' fields.
        """
        data = temperature_response.json()
        assert "average_temperature" in data
        assert "status" in data

    def test_temperature_endpoint_average_temperature_is_number(self, temperature_response):
        """Test that average_temperature is a numeric value.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The average_temperature is a float.
        """
        assert isinstance(temperature_response.json()["average_temperature"], (int, float))

    def test_temperature_endpoint_status_is_valid(self, temperature_response):
        """Test that status is one of the valid values.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The status is one of: 'Too Cold', 'Good', 'Too Hot'.
        """
        data = temperature_response.json()
        valid_statuses = ["Too Cold", "Good", "Too Hot"]
        assert data["status"] in valid_statuses


class TestMetricsEndpoint:
    """Test suite for the /metrics endpoint."""

    def test_metrics_endpoint_returns_200(self, metrics_response):
        """Test that /metrics returns HTTP 200 OK.
        
        Args:
            metrics_response: The response from the /metrics endpoint.
        
        Asserts:
            The response status code is 200.
        """
        assert metrics_response.status_code == 200

    def test_metrics_endpoint_returns_text(self, metrics_response):
        """Test that /metrics returns text content.
        
        Args:
            metrics_response: The response from the /metrics endpoint.
        
        Asserts:
            The response content type is text/plain.
        """
        assert "text/plain" in metrics_response.headers.get("Content-Type", "")

    def test_metrics_endpoint_returns_prometheus_format(self, metrics_response):
        """Test that /metrics returns Prometheus-formatted metrics.
        
        Args:
            metrics_response: The response from the /metrics endpoint.
        
        Asserts:
            The response contains Prometheus metric names.
        """
        content = metrics_response.text
        # Check for common Prometheus metric patterns
        assert any(pattern in content for pattern in [
            "hivebox_",
            "_total",
            "hivebox_requests_total",
        ])

    def test_metrics_endpoint_contains_temperature_metrics(self, metrics_response):
        """Test that /metrics contains temperature-related metrics.
        
        Args:
            metrics_response: The response from the /metrics endpoint.
        
        Asserts:
            The response contains temperature gauge metrics.
        """
        content = metrics_response.text
        assert "hivebox_temperature_celsius" in content
        assert "hivebox_temperature_status" in content


class TestEndpointHealth:
    """Test suite for general endpoint health checks."""

    def test_all_endpoints_accessible(self, client):
        """Test that all endpoints are accessible.
        
        Args:
            client: The base URL for the API.
        
        Asserts:
            All three endpoints return HTTP 200.
        """
        endpoints = [
            f"{client}/version",
            f"{client}/temperature",
            f"{client}/metrics",
        ]
        for endpoint in endpoints:
            response = requests.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} returned status {response.status_code}"

    def test_version_endpoint_does_not_crash(self, client):
        """Test that /version endpoint does not crash.
        
        Args:
            client: The base URL for the API.
        
        Asserts:
            The /version endpoint returns a valid response.
        """
        response = requests.get(f"{client}/version")
        assert response.status_code == 200

    def test_temperature_endpoint_does_not_crash(self, client):
        """Test that /temperature endpoint does not crash.
        
        Args:
            client: The base URL for the API.
        
        Asserts:
            The /temperature endpoint returns a valid response.
        """
        response = requests.get(f"{client}/temperature")
        assert response.status_code == 200

    def test_metrics_endpoint_does_not_crash(self, client):
        """Test that /metrics endpoint does not crash.
        
        Args:
            client: The base URL for the API.
        
        Asserts:
            The /metrics endpoint returns a valid response.
        """
        response = requests.get(f"{client}/metrics")
        assert response.status_code == 200


class TestResponseValidation:
    """Test suite for response validation."""

    def test_version_response_is_valid_json(self, version_response):
        """Test that /version response is valid JSON.
        
        Args:
            version_response: The response from the /version endpoint.
        
        Asserts:
            The response can be parsed as JSON.
        """
        try:
            json_data = version_response.json()
            assert isinstance(json_data, dict)
        except ValueError:
            pytest.fail("/version endpoint did not return valid JSON")

    def test_temperature_response_is_valid_json(self, temperature_response):
        """Test that /temperature response is valid JSON.
        
        Args:
            temperature_response: The response from the /temperature endpoint.
        
        Asserts:
            The response can be parsed as JSON.
        """
        try:
            json_data = temperature_response.json()
            assert isinstance(json_data, dict)
        except ValueError:
            pytest.fail("/temperature endpoint did not return valid JSON")

    def test_metrics_response_is_not_empty(self, metrics_response):
        """Test that /metrics response is not empty.
        
        Args:
            metrics_response: The response from the /metrics endpoint.
        
        Asserts:
            The response contains some content.
        """
        assert len(metrics_response.text) > 0
