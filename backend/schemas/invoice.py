"""Invoice Pydantic schemas — API response serialization."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class RuleResultResponse(BaseModel):
    id: int
    rule_name: str
    result: str
    message: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None

    class Config:
        from_attributes = True


class ProcessingLogResponse(BaseModel):
    """Individual pipeline stage log entry."""
    id: int
    stage: str
    status: str
    duration_ms: Optional[int] = None
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LineItemResponse(BaseModel):
    """Extracted line item from invoice."""
    id: int
    description: Optional[str] = None
    quantity: float = 0.0
    unit_price: float = 0.0
    amount: float = 0.0

    class Config:
        from_attributes = True


class LinkedPOResponse(BaseModel):
    """Linked purchase order summary."""
    id: int
    po_number: str
    amount: float
    currency: str = "INR"
    status: str = "OPEN"

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Invoice detail response."""
    id: int
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    po_number: Optional[str] = None
    invoice_date: Optional[date] = None
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    currency: str = "INR"
    status: str = "PENDING_MANUAL_REVIEW"
    document_type: Optional[str] = None
    extraction_confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None
    explanation: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    rule_results: List[RuleResultResponse] = []
    processing_logs: List[ProcessingLogResponse] = []
    line_items: List[LineItemResponse] = []
    linked_pos: List[LinkedPOResponse] = []

    class Config:
        from_attributes = True


class InvoiceListItem(BaseModel):
    """Compact invoice item for lists."""
    id: int
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    status: str
    document_type: Optional[str] = None
    total: float = 0.0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
