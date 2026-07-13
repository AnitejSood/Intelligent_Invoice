"""Invoice repository — data access for invoices."""

from sqlalchemy.orm import Session
from backend.models.invoice import Invoice


class InvoiceRepository:
    """Encapsulates all invoice-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_all(self, skip: int = 0, limit: int = 20, search: str | None = None, status: str | None = None) -> list[Invoice]:
        query = self.db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)
        if search:
            from backend.models.vendor import Vendor
            query = query.outerjoin(Vendor).filter(
                (Invoice.invoice_number.ilike(f"%{search}%")) | 
                (Vendor.vendor_name.ilike(f"%{search}%"))
            )
        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def count(self, search: str | None = None, status: str | None = None) -> int:
        query = self.db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)
        if search:
            from backend.models.vendor import Vendor
            query = query.outerjoin(Vendor).filter(
                (Invoice.invoice_number.ilike(f"%{search}%")) | 
                (Vendor.vendor_name.ilike(f"%{search}%"))
            )
        return query.count()

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def update(self, invoice: Invoice) -> Invoice:
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def find_duplicate(self, vendor_id: int | None, invoice_number: str | None) -> Invoice | None:
        if not vendor_id or not invoice_number:
            return None
        return (
            self.db.query(Invoice)
            .filter(Invoice.vendor_id == vendor_id, Invoice.invoice_number == invoice_number)
            .first()
        )
