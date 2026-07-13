"""Dashboard Pydantic schemas — placeholder for Phase 3."""

from pydantic import BaseModel
from typing import Optional


class DashboardMetrics(BaseModel):
    """Dashboard summary metrics."""
    total_invoices: int = 0
    approved: int = 0
    rejected: int = 0
    pending: int = 0
    avg_processing_time_ms: float = 0.0
    approval_rate: float = 0.0


class DashboardResponse(BaseModel):
    """Full dashboard response."""
    success: bool = True
    data: Optional[DashboardMetrics] = None
