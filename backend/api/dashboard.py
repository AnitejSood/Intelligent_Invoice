"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.dashboard_repository import DashboardRepository
from backend.schemas.dashboard import DashboardResponse, DashboardMetrics
from backend.schemas.invoice import InvoiceListItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """Return dashboard metrics."""
    repo = DashboardRepository(db)
    counts = repo.get_counts()
    avg_time = repo.get_avg_processing_time()
    recent = repo.get_recent_invoices(limit=5)
    
    total = counts["total_invoices"]
    approval_rate = (counts["approved"] / total * 100) if total > 0 else 0.0

    recent_items = [
        InvoiceListItem.model_validate(inv)
        for inv in recent
    ]

    metrics = DashboardMetrics(
        total_invoices=total,
        approved=counts["approved"],
        rejected=counts["rejected"],
        pending=counts["pending"],
        avg_processing_time_ms=avg_time,
        approval_rate=round(approval_rate, 1),
    )

    return DashboardResponse(
        success=True,
        data=metrics
    )


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Return chart-ready analytics."""
    repo = DashboardRepository(db)
    counts = repo.get_counts()
    total = counts["total_invoices"]
    approval_rate = (counts["approved"] / total * 100) if total > 0 else 0.0

    # For MVP, mock the trend data based on current counts
    return {
        "success": True,
        "data": {
            "approval_rate": round(approval_rate, 1),
            "status_distribution": [
                {"status": "Approved", "count": counts["approved"]},
                {"status": "Rejected", "count": counts["rejected"]},
                {"status": "Pending", "count": counts["pending"]},
            ],
            "processing_trend": [
                {"date": "Mon", "count": int(total * 0.1), "avg_time": avg_time if (avg_time:=repo.get_avg_processing_time()) else 2000},
                {"date": "Tue", "count": int(total * 0.2), "avg_time": 2500},
                {"date": "Wed", "count": int(total * 0.15), "avg_time": 2100},
                {"date": "Thu", "count": int(total * 0.25), "avg_time": 2800},
                {"date": "Fri", "count": int(total * 0.3), "avg_time": 1900},
            ],
        }
    }
