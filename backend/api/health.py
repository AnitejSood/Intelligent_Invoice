"""Health check endpoint."""

from fastapi import APIRouter

from backend.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Return service health status."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }
