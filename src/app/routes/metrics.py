"""Prometheus metrics module for HiveBox application."""

import logging

from fastapi import APIRouter, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

logger = logging.getLogger(__name__)
router = APIRouter()

REQUEST_COUNT = Counter(
    "hivebox_requests_total",
    "Total number of requests",
    ["endpoint", "method"],
)

CURRENT_TEMPERATURE = Gauge(
    "hivebox_temperature_celsius",
    "Current temperature reading in Celsius",
    ["box_id"],
)

TEMP_STATUS = Gauge(
    "hivebox_temperature_status",
    "Temperature status (0=Too Cold, 1=Good, 2=Too Hot)",
    ["box_id"],
)

TEMPERATURE_HISTOGRAM = Histogram(
    "hivebox_temperature_seconds",
    "Temperature reading distribution",
    ["box_id"],
    buckets=(0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 100.0),
)

TEMP_READINGS_COUNT = Counter(
    "hivebox_temperature_readings_total",
    "Total number of temperature readings collected",
    ["box_id"],
)

TEMP_ENDPOINT_REQUESTS = Counter(
    "hivebox_temperature_endpoint_requests_total",
    "Total requests to temperature endpoint",
)

METRICS_ENDPOINT_REQUESTS = Counter(
    "hivebox_metrics_endpoint_requests_total",
    "Total requests to metrics endpoint",
)

HEALTHY_BOXES_COUNT = Gauge(
    "hivebox_healthy_boxes_total",
    "Number of senseBoxes currently reachable",
)

CACHE_MISS_COUNT = Counter(
    "hivebox_cache_miss_total",
    "Total number of times data was fetched from external API"
    " due to cache miss or expiry",
)


@router.get("/metrics")
def get_metrics():
    """Expose Prometheus metrics endpoint."""
    logger.info("Metrics endpoint requested")
    METRICS_ENDPOINT_REQUESTS.inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
