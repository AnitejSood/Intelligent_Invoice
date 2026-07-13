"""Purchase order repository — data access for POs."""

from sqlalchemy.orm import Session
from backend.models.purchase_order import PurchaseOrder


class PurchaseOrderRepository:
    """Encapsulates purchase order database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, po_id: int) -> PurchaseOrder | None:
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()

    def get_by_po_number(self, po_number: str) -> PurchaseOrder | None:
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()

    def find_by_po_number_fuzzy(self, po_number: str) -> PurchaseOrder | None:
        """Try exact match first, then case-insensitive partial match."""
        exact = self.get_by_po_number(po_number)
        if exact:
            return exact
        return (
            self.db.query(PurchaseOrder)
            .filter(PurchaseOrder.po_number.ilike(f"%{po_number}%"))
            .first()
        )

    def get_open_pos_for_vendor(self, vendor_id: int) -> list[PurchaseOrder]:
        """Get all OPEN purchase orders for a given vendor."""
        return (
            self.db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.vendor_id == vendor_id,
                PurchaseOrder.status == "OPEN",
            )
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 20) -> list[PurchaseOrder]:
        return self.db.query(PurchaseOrder).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(PurchaseOrder).count()
