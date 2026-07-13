"""Settings API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingsUpdateSchema(BaseModel):
    PO_TOLERANCE_PERCENT: float
    MAX_INVOICE_AGE_DAYS: int
    REQUIRE_GST: bool
    REQUIRE_PO: bool
    USE_LOCAL_OCR: bool = False
    DUPLICATE_DETECTION_DAYS: int = 90
    MIN_CONFIDENCE_THRESHOLD: int = 85
    REQUIRE_LINE_ITEMS_MATCH: bool = True
    EMAIL_INGESTION_ENABLED: bool = False
    EMAIL_SERVER: str = "imap.gmail.com"
    EMAIL_ADDRESS: str = ""
    EMAIL_PASSWORD: str = ""
    ERP_SYNC_ENABLED: bool = False
    ERP_WEBHOOK_URL: str = ""

@router.get("")
async def get_settings():
    """Retrieve dynamic settings configuration."""
    return {
        "success": True,
        "data": SettingsService.get_all()
    }

@router.post("")
async def update_settings(payload: SettingsUpdateSchema):
    """Update dynamic settings configuration."""
    success = SettingsService.save(payload.model_dump())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to persist settings")
    return {
        "success": True,
        "message": "Settings updated successfully",
        "data": SettingsService.get_all()
    }
