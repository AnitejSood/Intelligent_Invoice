"""Invoice API endpoints."""

import os
import json
import shutil
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.invoice_repository import InvoiceRepository
from backend.repositories.vendor_repository import VendorRepository
from backend.repositories.purchase_order_repository import PurchaseOrderRepository
from backend.schemas.common import PaginatedResponse
from backend.schemas.invoice import InvoiceResponse, InvoiceListItem, LinkedPOResponse

from backend.services.ocr_service import OCRService
from backend.services.gemini_service import GeminiService
from backend.services.validation_service import ValidationService
from backend.services.decision_service import DecisionService
from backend.models.invoice import Invoice
from backend.models.line_item import InvoiceLineItem
from backend.models.rule_result import RuleResult as DB_RuleResult
from backend.models.processing_log import ProcessingLog
from backend.models.invoice_purchase_order import invoice_purchase_orders

from backend.core.logging_config import get_logger

logger = get_logger("api.invoices")

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def _log_stage(db: Session, invoice_id: int, stage: str, status: str,
               duration_ms: int = 0, metadata: dict | None = None) -> ProcessingLog:
    """Helper to create and persist a processing log entry."""
    log = ProcessingLog(
        invoice_id=invoice_id,
        stage=stage,
        status=status,
        duration_ms=duration_ms,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(log)
    db.flush()
    return log


@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process an invoice end-to-end with full processing timeline."""
    from backend.services.pipeline_service import PipelineService
    
    # ──────────────────────────────────────────────────
    # Stage 1: File Upload & Save to Disk
    # ──────────────────────────────────────────────────
    from backend.core.config import settings
    os.makedirs(settings.upload_path, exist_ok=True)
    file_path = str(settings.upload_path / file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ──────────────────────────────────────────────────
    # Execute Full Pipeline
    # ──────────────────────────────────────────────────
    invoice, pipeline_summary, matched_pos = PipelineService.process_invoice_file(
        db=db,
        file_path=file_path,
        original_filename=file.filename,
        source="UPLOAD"
    )

    # Build response with linked POs
    response_data = InvoiceResponse.model_validate(invoice)
    response_data.linked_pos = [
        LinkedPOResponse(
            id=po.id,
            po_number=po.po_number,
            amount=po.amount,
            currency=po.currency,
            status=po.status,
        ) for po in matched_pos
    ]

    return {
        "success": True, 
        "message": "Upload successful", 
        "data": response_data,
        "pipeline_summary": pipeline_summary
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get full invoice details."""
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    response = InvoiceResponse.model_validate(invoice)
    # Attach linked POs from the many-to-many relationship
    if invoice.purchase_orders:
        response.linked_pos = [
            LinkedPOResponse(
                id=po.id,
                po_number=po.po_number,
                amount=po.amount,
                currency=po.currency,
                status=po.status,
            ) for po in invoice.purchase_orders
        ]
    return response


@router.get("", response_model=PaginatedResponse)
async def list_invoices(
    skip: int = 0, 
    limit: int = 20, 
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """List invoices with pagination, search, and status filtering."""
    repo = InvoiceRepository(db)
    total = repo.count(search=search, status=status)
    invoices = repo.get_all(skip=skip, limit=limit, search=search, status=status)
    
    items = [InvoiceListItem.model_validate(inv) for inv in invoices]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        limit=limit
    )


@router.post("/{invoice_id}/reprocess")
async def reprocess_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Reprocess an invoice."""
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    invoice.status = "PENDING_MANUAL_REVIEW"
    invoice.explanation = "Reprocessing requested."
    repo.update(invoice)
    
    return {"success": True, "message": "Invoice flagged for reprocessing."}
