"""Invoice Line Item model."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.base import Base


class InvoiceLineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String)
    quantity = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")

    def __repr__(self) -> str:
        return f"<LineItem(id={self.id}, desc='{self.description}', amount={self.amount})>"
