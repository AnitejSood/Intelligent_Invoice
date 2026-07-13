"""Dashboard repository — aggregate queries for dashboard metrics."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.invoice import Invoice


class DashboardRepository:
    """Aggregate queries for dashboard data."""

    def __init__(self, db: Session):
        self.db = db

    def get_counts(self) -> dict:
        """Get invoice status counts."""
        total = self.db.query(Invoice).count()
        approved = self.db.query(Invoice).filter(Invoice.status == "APPROVED").count()
        rejected = self.db.query(Invoice).filter(Invoice.status == "REJECTED").count()
        pending = self.db.query(Invoice).filter(Invoice.status == "PENDING_MANUAL_REVIEW").count()
        return {
            "total_invoices": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
        }

    def get_avg_processing_time(self) -> float:
        """Average processing time across all invoices."""
        result = self.db.query(func.avg(Invoice.processing_time_ms)).scalar()
        return round(result or 0, 1)

    def get_recent_invoices(self, limit: int = 10) -> list[Invoice]:
        """Most recently processed invoices."""
        return (
            self.db.query(Invoice)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
            .all()
        )
