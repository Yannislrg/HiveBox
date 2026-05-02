"""HiveBox application entry point."""

from fastapi import FastAPI

from src.app.routes.version import router as version_router
from src.app.routes.temperature import get_avg_temperature


app = FastAPI(title="HiveBox")
app.include_router(version_router)
app.add_api_route("/temperature", get_avg_temperature, methods=["GET"])
app.add_api_route("/version", get_avg_temperature, methods=["GET"])
