from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# Forward references for relations
class InvoiceMinimal(BaseModel):
    id: int
    invoice_number: str
    status: str
    total: float
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VendorMinimal(BaseModel):
    id: int
    vendor_name: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderBase(BaseModel):
    po_number: str
    vendor_id: int
    amount: float
    currency: str = "INR"
    status: str = "OPEN"

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    created_at: datetime
    
    vendor: Optional[VendorMinimal] = None
    linked_invoices: List[InvoiceMinimal] = []
    
    model_config = ConfigDict(from_attributes=True)
