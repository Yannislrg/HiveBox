"""Version endpoint for HiveBox."""

from fastapi import APIRouter


VERSION = "v0.0.1"

router = APIRouter()


@router.get("/version")
def get_version() -> dict[str, str]:
    """Return the current deployed application version."""
    return {"version": VERSION}
