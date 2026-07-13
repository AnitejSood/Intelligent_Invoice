"""Invoice ↔ PurchaseOrder many-to-many association table."""

from sqlalchemy import Column, Integer, Float, ForeignKey, Table
from backend.database.base import Base

# Association table for many-to-many: one invoice can link to multiple POs,
# and one PO can have multiple invoices billed against it.
invoice_purchase_orders = Table(
    "invoice_purchase_orders",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("invoice_id", Integer, ForeignKey("invoices.id"), nullable=False),
    Column("po_id", Integer, ForeignKey("purchase_orders.id"), nullable=False),
    Column("allocated_amount", Float, default=0.0),
)
