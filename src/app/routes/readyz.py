from fastapi import APIRouter, Response, status
from src.app.services.sensor_service import sensor_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/readyz")
def readiness_check():
    """Readiness probe with complex availability logic.
    
    Returns 200 if healthy, 503 if unhealthy.
    """
    if sensor_service.is_healthy():
        return Response(status_code=status.HTTP_200_OK)

    logger.error("Readiness probe failed: majority of boxes unreachable and cache is stale")
    return Response(
        content="Service Unhealthy: mayoría de sensores inalcanzables y caché expirada",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )
