"""Invoice model — core entity for processed invoices."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database.base import Base
from backend.models.invoice_purchase_order import invoice_purchase_orders


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)  # primary PO (legacy compat)
    invoice_date = Column(Date, nullable=True)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    shipping = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    status = Column(String, default="PENDING_MANUAL_REVIEW")  # APPROVED | REJECTED | PENDING_MANUAL_REVIEW
    document_type = Column(String)  # DIGITAL | SCANNED
    extraction_confidence = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON string of raw extraction
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    purchase_order = relationship("PurchaseOrder", back_populates="invoices", foreign_keys=[po_id])
    purchase_orders = relationship(
        "PurchaseOrder",
        secondary=invoice_purchase_orders,
        back_populates="linked_invoices",
        lazy="selectin",
    )
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    rule_results = relationship("RuleResult", back_populates="invoice", cascade="all, delete-orphan")
    processing_logs = relationship("ProcessingLog", back_populates="invoice", cascade="all, delete-orphan", order_by="ProcessingLog.created_at")

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"

    @property
    def vendor_name(self) -> str | None:
        return self.vendor.vendor_name if self.vendor else None

    @property
    def po_number(self) -> str | None:
        """Return primary PO number, or comma-separated list if multi-PO."""
        if self.purchase_orders:
            return ", ".join(po.po_number for po in self.purchase_orders)
        if self.purchase_order:
            return self.purchase_order.po_number
        return None
