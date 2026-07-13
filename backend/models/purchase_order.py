"""Purchase Order model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_number = Column(String, unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="OPEN")  # OPEN | CLOSED | CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    # Legacy 1:N relationship
    invoices = relationship("Invoice", back_populates="purchase_order")
    # Modern M:N relationship
    from backend.models.invoice import invoice_purchase_orders
    linked_invoices = relationship(
        "Invoice", 
        secondary=invoice_purchase_orders, 
        back_populates="purchase_orders"
    )

    def __repr__(self) -> str:
        return f"<PurchaseOrder(id={self.id}, po='{self.po_number}', amount={self.amount})>"
