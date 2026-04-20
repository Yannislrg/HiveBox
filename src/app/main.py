"""HiveBox application entry point."""

from fastapi import FastAPI

from src.app.routes.version import router as version_router


app = FastAPI(title="HiveBox")
app.include_router(version_router)
