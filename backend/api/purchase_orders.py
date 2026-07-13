"""Purchase Order API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload, selectinload

from backend.database.session import get_db
from backend.repositories.purchase_order_repository import PurchaseOrderRepository
from backend.schemas.common import PaginatedResponse
from backend.schemas.purchase_order import PurchaseOrderResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("", response_model=PaginatedResponse)
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Return purchase orders with pagination and relations."""
    from backend.models.purchase_order import PurchaseOrder
    
    total = db.query(PurchaseOrder).count()
    
    # Use selectinload for many-to-many to avoid cartesian explosion, joinedload for N:1
    pos = (
        db.query(PurchaseOrder)
        .options(
            joinedload(PurchaseOrder.vendor),
            selectinload(PurchaseOrder.linked_invoices)
        )
        .order_by(PurchaseOrder.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    items = [PurchaseOrderResponse.model_validate(po) for po in pos]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        limit=limit
    )
