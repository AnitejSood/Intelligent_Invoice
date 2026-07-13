"""Vendor API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.vendor_repository import VendorRepository
from backend.schemas.common import PaginatedResponse
from backend.schemas.vendor import VendorResponse, VendorUpdateStatus

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("", response_model=PaginatedResponse)
async def list_vendors(db: Session = Depends(get_db)):
    """Return all vendors."""
    repo = VendorRepository(db)
    vendors = repo.get_all()
    
    items = [VendorResponse.model_validate(v) for v in vendors]
    
    return PaginatedResponse(
        items=items,
        total=len(items),
        page=1,
        limit=len(items)
    )


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Get vendor details."""
    repo = VendorRepository(db)
    vendor = repo.get_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    return VendorResponse.model_validate(vendor)


@router.put("/{vendor_id}/status", response_model=VendorResponse)
async def update_vendor_status(
    vendor_id: int, 
    update_data: VendorUpdateStatus, 
    db: Session = Depends(get_db)
):
    """Update vendor status."""
    repo = VendorRepository(db)
    vendor = repo.update_status(vendor_id, update_data.status)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    return VendorResponse.model_validate(vendor)
