"""HiveBox application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.routes.version import router as version_router
from src.app.routes.temperature import router as get_avg_temperature
from src.app.routes.metrics import router as metrics_router
from src.app.routes.readyz import router as readyz_router
from src.app.routes.store import router as store_router
from src.app.services.sensor_service import sensor_service
from src.app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


async def periodic_storage():
    """Background task to store sensor data every 5 minutes."""
    while True:
        try:
            logger.info("Starting periodic data storage")
            data = sensor_service.get_data()
            if data:
                storage_service.store_data(data)
                logger.info("Periodic storage successful")
            else:
                logger.warning("No data available for periodic storage")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Periodic storage task failed: %s", e)

        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifecycle events for the FastAPI application."""
    storage_task = asyncio.create_task(periodic_storage())
    yield
    storage_task.cancel()
    try:
        await storage_task
    except asyncio.CancelledError:
        logger.info("Periodic storage task cancelled")


app = FastAPI(title="HiveBox", lifespan=lifespan)
app.include_router(version_router)
app.include_router(get_avg_temperature)
app.include_router(metrics_router)
app.include_router(readyz_router)
app.include_router(store_router)
