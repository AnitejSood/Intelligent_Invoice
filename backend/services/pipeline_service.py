"""Core AI Pipeline Service."""

import os
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session

from backend.repositories.invoice_repository import InvoiceRepository
from backend.repositories.vendor_repository import VendorRepository
from backend.repositories.purchase_order_repository import PurchaseOrderRepository
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

logger = get_logger("services.pipeline")


class PipelineService:
    """Core AI Pipeline Service for processing invoices from any source."""

    @staticmethod
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

    @staticmethod
    def process_invoice_file(db: Session, file_path: str, original_filename: str, source: str = "UPLOAD") -> tuple[Invoice, dict, list]:
        """
        Process a saved invoice file end-to-end.
        Returns (Invoice, pipeline_summary, matched_pos).
        """
        pipeline_start = time.time()
        
        # ──────────────────────────────────────────────────
        # Stage 1: Ingest Logging
        # ──────────────────────────────────────────────────
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        # Create a placeholder invoice to attach logs to
        placeholder = Invoice(
            invoice_number=f"PROCESSING-{original_filename}",
            status="PROCESSING",
            file_path=file_path,
        )
        db.add(placeholder)
        db.flush()

        PipelineService._log_stage(db, placeholder.id, f"File Ingest ({source})", "COMPLETED", 0, {
            "filename": original_filename,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2) if file_size else 0,
        })

        # ──────────────────────────────────────────────────
        # Stage 2: OCR Pipeline (Document Detection + Text Extraction)
        # ──────────────────────────────────────────────────
        from backend.core.config import settings
        t0 = time.time()
        
        extracted_text = ""
        confidence = 0.0
        doc_type = "UNKNOWN"
        images = None
        
        if settings.USE_LOCAL_OCR:
            doc_type, extracted_text, confidence = OCRService.process_document(file_path)
            ocr_ms = int((time.time() - t0) * 1000)
            PipelineService._log_stage(db, placeholder.id, "Local OCR Processing", "COMPLETED", ocr_ms, {
                "document_type": doc_type,
                "extraction_confidence": round(confidence, 4),
                "characters_extracted": len(extracted_text),
                "text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            })
        else:
            # Use Gemini Multimodal Vision (Bypass local OCR)
            from backend.ocr.document_detector import DocumentDetector
            doc_type = DocumentDetector.detect_type(file_path)
            if doc_type == "DIGITAL":
                from backend.ocr.pdf_extractor import PDFExtractor
                extracted_text = PDFExtractor.extract_text(file_path)
                confidence = 1.0
            else:
                # SCANNED - convert to images and skip text extraction
                images = OCRService.convert_pdf_to_images(file_path)
                confidence = 0.95 # Assumed high confidence for Gemini Vision
                extracted_text = ""
            
            ocr_ms = int((time.time() - t0) * 1000)
            PipelineService._log_stage(db, placeholder.id, "Document Detection (Vision Mode)", "COMPLETED", ocr_ms, {
                "document_type": doc_type,
                "image_count": len(images) if images else 0,
                "note": "Local OCR skipped. Delegating to Gemini Vision."
            })

        # ──────────────────────────────────────────────────
        # Stage 3: Gemini AI Semantic Extraction
        # ──────────────────────────────────────────────────
        t0 = time.time()
        extracted_data = GeminiService.extract_data(text=extracted_text, images=images)
        gemini_ms = int((time.time() - t0) * 1000)

        fields_found = sum(1 for v in [
            extracted_data.invoice_number, extracted_data.vendor_name,
            extracted_data.invoice_date, extracted_data.po_number,
            extracted_data.total, extracted_data.vendor_gst,
        ] if v)

        PipelineService._log_stage(db, placeholder.id, "AI Semantic Extraction", "COMPLETED", gemini_ms, {
            "fields_extracted": fields_found,
            "invoice_number": extracted_data.invoice_number,
            "vendor_name": extracted_data.vendor_name,
            "po_number": extracted_data.po_number,
            "po_numbers": extracted_data.po_numbers,
            "total": extracted_data.total,
            "line_items_count": len(extracted_data.line_items),
        })

        # ──────────────────────────────────────────────────
        # Stage 4: Context Lookup (Vendor + PO Matching)
        # ──────────────────────────────────────────────────
        t0 = time.time()
        repo = InvoiceRepository(db)
        vendor_repo = VendorRepository(db)
        po_repo = PurchaseOrderRepository(db)

        context = {}
        vendor = None
        vendor_match_detail = "No vendor extracted"

        if extracted_data.vendor_name:
            vendor = vendor_repo.find_by_name_fuzzy(extracted_data.vendor_name)
            if vendor:
                context["vendor"] = vendor
                vendor_match_detail = f"Matched: '{extracted_data.vendor_name}' → '{vendor.vendor_name}' (ID: {vendor.id}, Status: {vendor.status})"
            else:
                vendor_match_detail = f"No match found for '{extracted_data.vendor_name}'"

        # Multi-PO matching
        matched_pos = []
        po_match_details = []

        po_numbers_to_check = extracted_data.po_numbers or ([extracted_data.po_number] if extracted_data.po_number else [])
        
        for po_num in po_numbers_to_check:
            if not po_num:
                continue
            po = po_repo.find_by_po_number_fuzzy(po_num)
            if po:
                matched_pos.append(po)
                po_match_details.append(f"✓ {po_num} → {po.po_number} (₹{po.amount:,.2f}, {po.status})")
            else:
                po_match_details.append(f"✗ {po_num} → Not found in system")

        if not matched_pos and vendor:
            vendor_open_pos = po_repo.get_open_pos_for_vendor(vendor.id)
            if vendor_open_pos:
                po_match_details.append(f"Fallback: Found {len(vendor_open_pos)} open POs for vendor")
                if extracted_data.total > 0:
                    for vpo in vendor_open_pos:
                        tolerance = vpo.amount * 0.1
                        if abs(vpo.amount - extracted_data.total) <= tolerance:
                            matched_pos.append(vpo)
                            po_match_details.append(f"✓ Auto-matched by amount: {vpo.po_number} (₹{vpo.amount:,.2f})")

        primary_po = matched_pos[0] if matched_pos else None
        if primary_po:
            context["po"] = primary_po
        if matched_pos:
            context["matched_pos"] = matched_pos

        if extracted_data.invoice_number and vendor:
            existing = db.query(Invoice).filter(
                Invoice.invoice_number == extracted_data.invoice_number,
                Invoice.vendor_id == vendor.id,
                Invoice.id != placeholder.id,
            ).first()
            if existing:
                context["is_duplicate"] = True

        lookup_ms = int((time.time() - t0) * 1000)
        PipelineService._log_stage(db, placeholder.id, "Context Lookup", "COMPLETED", lookup_ms, {
            "vendor_match": vendor_match_detail,
            "po_matches": po_match_details,
            "po_count": len(matched_pos),
            "is_duplicate": context.get("is_duplicate", False),
        })

        # ──────────────────────────────────────────────────
        # Stage 5: Deterministic Rule Engine
        # ──────────────────────────────────────────────────
        t0 = time.time()
        rule_results = ValidationService.run_all_rules(extracted_data, context)
        rules_ms = int((time.time() - t0) * 1000)

        pass_count = sum(1 for r in rule_results if r.result == "PASS")
        fail_count = sum(1 for r in rule_results if r.result == "FAIL")

        PipelineService._log_stage(db, placeholder.id, "Rule Engine Evaluation", "COMPLETED", rules_ms, {
            "total_rules": len(rule_results),
            "passed": pass_count,
            "failed": fail_count,
            "rule_summary": [{"name": r.rule_name, "result": r.result} for r in rule_results],
        })

        # ──────────────────────────────────────────────────
        # Stage 6: Decision Engine
        # ──────────────────────────────────────────────────
        t0 = time.time()
        decision = DecisionService.determine_status(rule_results, confidence)
        decision_ms = int((time.time() - t0) * 1000)

        PipelineService._log_stage(db, placeholder.id, "Decision Engine", "COMPLETED", decision_ms, {
            "decision": decision,
            "extraction_confidence": round(confidence, 4),
            "failures_count": fail_count,
        })

        # ──────────────────────────────────────────────────
        # Stage 7: AI Explanation Generation
        # ──────────────────────────────────────────────────
        t0 = time.time()
        explanation = GeminiService.explain_decision(
            extracted_data, 
            rule_results, 
            decision,
            doc_type=doc_type,
            confidence=confidence,
            vendor_match=vendor_match_detail,
        )
        explain_ms = int((time.time() - t0) * 1000)

        PipelineService._log_stage(db, placeholder.id, "AI Explanation", "COMPLETED", explain_ms, {
            "explanation_length": len(explanation),
        })

        # ──────────────────────────────────────────────────
        # Stage 8: Persist to Database
        # ──────────────────────────────────────────────────
        t0 = time.time()

        parsed_date = None
        if extracted_data.invoice_date:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    parsed_date = datetime.strptime(extracted_data.invoice_date, fmt).date()
                    break
                except ValueError:
                    continue

        total_ms = int((time.time() - pipeline_start) * 1000)

        placeholder.invoice_number = extracted_data.invoice_number or f"UNKNOWN-{original_filename}"
        placeholder.vendor_id = vendor.id if vendor else None
        placeholder.po_id = primary_po.id if primary_po else None
        placeholder.invoice_date = parsed_date
        placeholder.subtotal = extracted_data.subtotal
        placeholder.tax = extracted_data.tax
        placeholder.total = extracted_data.total
        placeholder.currency = extracted_data.currency
        placeholder.status = decision
        placeholder.document_type = doc_type
        placeholder.extraction_confidence = confidence
        placeholder.processing_time_ms = total_ms
        placeholder.explanation = explanation
        placeholder.extracted_data = extracted_data.model_dump_json()

        for item in extracted_data.line_items:
            db_item = InvoiceLineItem(
                invoice_id=placeholder.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
            )
            db.add(db_item)

        for res in rule_results:
            db_res = DB_RuleResult(
                invoice_id=placeholder.id,
                rule_name=res.rule_name,
                result=res.result,
                message=res.message,
                expected=res.expected,
                actual=res.actual
            )
            db.add(db_res)

        for po in matched_pos:
            db.execute(invoice_purchase_orders.insert().values(
                invoice_id=placeholder.id,
                po_id=po.id,
                allocated_amount=float(po.amount),
            ))

        save_ms = int((time.time() - t0) * 1000)
        PipelineService._log_stage(db, placeholder.id, "Database Persist", "COMPLETED", save_ms, {
            "rule_results_saved": len(rule_results),
            "line_items_saved": len(extracted_data.line_items),
            "po_links_saved": len(matched_pos),
        })

        db.commit()
        db.refresh(placeholder)
        
        pipeline_summary = {
            "total_time_ms": total_ms,
            "document_type": doc_type,
            "confidence": round(confidence, 4),
            "fields_extracted": fields_found,
            "rules_passed": pass_count,
            "rules_failed": fail_count,
            "decision": decision,
            "po_count": len(matched_pos),
        }

        return placeholder, pipeline_summary, matched_pos
