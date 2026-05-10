"""Pytest configuration for HiveBox integration tests.

This module provides fixtures for running integration tests against the Docker container.
"""

import time
from typing import Optional

import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for the API endpoint.
    
    Returns:
        str: The base URL where the API is running.
    """
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def version_endpoint(api_base_url):
    """Version endpoint URL.
    
    Args:
        api_base_url: The base URL for the API.
    
    Returns:
        str: The full URL for the version endpoint.
    """
    return f"{api_base_url}/version"


@pytest.fixture(scope="session")
def temperature_endpoint(api_base_url):
    """Temperature endpoint URL.
    
    Args:
        api_base_url: The base URL for the API.
    
    Returns:
        str: The full URL for the temperature endpoint.
    """
    return f"{api_base_url}/temperature"


@pytest.fixture(scope="session")
def metrics_endpoint(api_base_url):
    """Metrics endpoint URL.
    
    Args:
        api_base_url: The base URL for the API.
    
    Returns:
        str: The full URL for the metrics endpoint.
    """
    return f"{api_base_url}/metrics"


@pytest.fixture(scope="session")
def version_response(version_endpoint):
    """Get the version endpoint response.
    
    Args:
        version_endpoint: The URL for the version endpoint.
    
    Returns:
        requests.Response: The response from the /version endpoint.
    """
    return requests.get(version_endpoint)


@pytest.fixture(scope="session")
def temperature_response(temperature_endpoint):
    """Get the temperature endpoint response.
    
    Args:
        temperature_endpoint: The URL for the temperature endpoint.
    
    Returns:
        requests.Response: The response from the /temperature endpoint.
    """
    return requests.get(temperature_endpoint)


@pytest.fixture(scope="session")
def metrics_response(metrics_endpoint):
    """Get the metrics endpoint response.
    
    Args:
        metrics_endpoint: The URL for the metrics endpoint.
    
    Returns:
        requests.Response: The response from the /metrics endpoint.
    """
    return requests.get(metrics_endpoint)


@pytest.fixture(scope="session")
def all_responses(
    version_endpoint,
    temperature_endpoint,
    metrics_endpoint,
):
    """Get responses from all endpoints.
    
    Args:
        version_endpoint: The URL for the version endpoint.
        temperature_endpoint: The URL for the temperature endpoint.
        metrics_endpoint: The URL for the metrics endpoint.
    
    Returns:
        dict: A dictionary containing responses from all endpoints.
    """
    return {
        "version": requests.get(version_endpoint),
        "temperature": requests.get(temperature_endpoint),
        "metrics": requests.get(metrics_endpoint),
    }


@pytest.fixture(scope="session")
def version_json(version_response):
    """Get the version JSON data.
    
    Args:
        version_response: The response from the /version endpoint.
    
    Returns:
        dict: The parsed JSON data from the version endpoint.
    """
    return version_response.json()


@pytest.fixture(scope="session")
def temperature_json(temperature_response):
    """Get the temperature JSON data.
    
    Args:
        temperature_response: The response from the /temperature endpoint.
    
    Returns:
        dict: The parsed JSON data from the temperature endpoint.
    """
    return temperature_response.json()


@pytest.fixture(scope="session")
def metrics_text(metrics_response):
    """Get the metrics text content.
    
    Args:
        metrics_response: The response from the /metrics endpoint.
    
    Returns:
        str: The text content from the metrics endpoint.
    """
    return metrics_response.text


@pytest.fixture(scope="session")
def all_json(all_responses):
    """Get JSON data from all endpoints.
    
    Args:
        all_responses: Responses from all endpoints.
    
    Returns:
        dict: A dictionary containing parsed JSON from all endpoints.
    """
    return {
        "version": all_responses["version"].json(),
        "temperature": all_responses["temperature"].json(),
    }
