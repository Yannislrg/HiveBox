"""HiveBox application entry point."""

from fastapi import FastAPI

from src.app.routes.version import router as version_router
from src.app.routes.temperature import router as get_avg_temperature


app = FastAPI(title="HiveBox")
app.include_router(version_router)
app.include_router(get_avg_temperature)
