"""Vendor repository — data access for vendors."""

from sqlalchemy.orm import Session
from backend.models.vendor import Vendor


class VendorRepository:
    """Encapsulates vendor-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vendor_id: int) -> Vendor | None:
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()

    def get_by_name(self, name: str) -> Vendor | None:
        return self.db.query(Vendor).filter(Vendor.vendor_name == name).first()

    def find_by_name_fuzzy(self, name: str) -> Vendor | None:
        """Case-insensitive partial match for vendor lookup."""
        return (
            self.db.query(Vendor)
            .filter(Vendor.vendor_name.ilike(f"%{name}%"))
            .first()
        )

    def get_by_gst(self, gst_number: str) -> Vendor | None:
        return self.db.query(Vendor).filter(Vendor.gst_number == gst_number).first()

    def get_all(self) -> list[Vendor]:
        return self.db.query(Vendor).all()

    def count(self) -> int:
        return self.db.query(Vendor).count()

    def update_status(self, vendor_id: int, status: str) -> Vendor | None:
        vendor = self.get_by_id(vendor_id)
        if vendor:
            vendor.status = status
            self.db.commit()
            self.db.refresh(vendor)
        return vendor
