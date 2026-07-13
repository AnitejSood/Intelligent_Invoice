"""Vendor model — approved suppliers in the system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.database.base import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_name = Column(String, unique=True, nullable=False, index=True)
    gst_number = Column(String, index=True)
    bank_account = Column(String)
    status = Column(String, default="APPROVED")  # APPROVED | BLACKLISTED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    invoices = relationship("Invoice", back_populates="vendor")

    def __repr__(self) -> str:
        return f"<Vendor(id={self.id}, name='{self.vendor_name}', status='{self.status}')>"
