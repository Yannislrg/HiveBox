import logging
from fastapi import APIRouter, HTTPException
from src.app.services.sensor_service import sensor_service
from src.app.services.storage_service import storage_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/store")
def store_sensor_data():
    """Trigger manual storage of sensor data to MinIO."""
    try:
        data = sensor_service.get_data()
        if not data:
            raise HTTPException(status_code=404, detail="No sensor data available to store")
        
        filename = storage_service.store_data(data)
        return {"message": "Data stored successfully", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual storage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
