"""Vendor Pydantic schemas — placeholder for Phase 3."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VendorResponse(BaseModel):
    """Vendor detail response."""
    id: int
    vendor_name: str
    gst_number: Optional[str] = None
    status: str = "APPROVED"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VendorUpdateStatus(BaseModel):
    status: str
