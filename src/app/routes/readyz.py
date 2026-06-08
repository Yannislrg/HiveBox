"""Readiness probe route for Kubernetes health checks."""

import logging

from fastapi import APIRouter, Response, status

from src.app.services.sensor_service import sensor_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/readyz")
def readiness_check():
    """Readiness probe: returns 200 if healthy, 503 if unhealthy."""
    if sensor_service.is_healthy():
        return Response(status_code=status.HTTP_200_OK)

    logger.error(
        "Readiness probe failed: majority of boxes unreachable"
        " and cache is stale"
    )
    msg = (
        "Service Unhealthy: majority of sensors unreachable and cache expired"
    )
    return Response(
        content=msg,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )
