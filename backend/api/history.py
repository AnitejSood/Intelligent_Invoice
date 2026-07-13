"""History API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.invoice_repository import InvoiceRepository
from backend.schemas.common import PaginatedResponse
from backend.schemas.invoice import InvoiceListItem

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=PaginatedResponse)
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Return invoice processing history with pagination."""
    repo = InvoiceRepository(db)
    
    total = repo.count()
    invoices = repo.get_all(skip=skip, limit=limit)
    
    items = [InvoiceListItem.model_validate(inv) for inv in invoices]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        limit=limit
    )
