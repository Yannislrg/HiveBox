"""Prometheus metrics module for HiveBox application."""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import APIRouter, Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Define Prometheus metrics
# Counter: increments for each request
REQUEST_COUNT = Counter(
    "hivebox_requests_total",
    "Total number of requests",
    ["endpoint", "method"],
)

# Gauge: current temperature reading
CURRENT_TEMPERATURE = Gauge(
    "hivebox_temperature_celsius",
    "Current temperature reading in Celsius",
    ["box_id"],
)

# Gauge: status indicator (0=Too Cold, 1=Good, 2=Too Hot)
TEMP_STATUS = Gauge(
    "hivebox_temperature_status",
    "Temperature status (0=Too Cold, 1=Good, 2=Too Hot)",
    ["box_id"],
)

# Histogram: distribution of temperature readings
TEMPERATURE_HISTOGRAM = Histogram(
    "hivebox_temperature_seconds",
    "Temperature reading distribution",
    ["box_id"],
    buckets=(0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 100.0),
)

# Counter: total temperature readings collected
TEMP_READINGS_COUNT = Counter(
    "hivebox_temperature_readings_total",
    "Total number of temperature readings collected",
    ["box_id"],
)

# Counter: requests to temperature endpoint
TEMP_ENDPOINT_REQUESTS = Counter(
    "hivebox_temperature_endpoint_requests_total",
    "Total requests to temperature endpoint",
)

# Counter: requests to metrics endpoint
METRICS_ENDPOINT_REQUESTS = Counter(
    "hivebox_metrics_endpoint_requests_total",
    "Total requests to metrics endpoint",
)


@router.get("/metrics")
def get_metrics():
    """Expose Prometheus metrics endpoint.

    Returns:
        Response: Prometheus-formatted metrics
    """
    logger.info("Metrics endpoint requested")
    METRICS_ENDPOINT_REQUESTS.inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
