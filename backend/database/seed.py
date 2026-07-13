"""FinanceFlow AI — Database Seed Script

Seeds the database with deterministic, purpose-built vendor and PO data
that aligns with the 8 edge-case test invoices.
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker

from backend.database.session import SessionLocal
from backend.models import (
    Vendor, PurchaseOrder, Invoice, InvoiceLineItem,
    RuleResult, ProcessingLog
)

fake = Faker("en_IN")


def get_random_gst():
    """Generate a realistic looking GST number."""
    state_code = str(random.randint(10, 37))
    pan = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5)) + \
          "".join(random.choices("0123456789", k=4)) + \
          random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    entity_code = str(random.randint(1, 9))
    checksum = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return f"{state_code}{pan}{entity_code}Z{checksum}"


# ────────────────────────────────────────────────────────────
# Core Vendors — deterministic, match test invoice scenarios
# ────────────────────────────────────────────────────────────
CORE_VENDORS = [
    {"name": "AWS India Pvt Ltd", "gst": "29AABCU9603R1ZM", "status": "APPROVED"},
    {"name": "Google Cloud India", "gst": "29AABCG7890R1ZK", "status": "APPROVED"},
    {"name": "Microsoft Corporation India", "gst": "27AABCM1234F1ZP", "status": "APPROVED"},
    {"name": "Atlassian Pty Ltd", "gst": "06AABCA5678Q1ZN", "status": "APPROVED"},
    {"name": "Slack Technologies", "gst": "27AABCS9012T1ZR", "status": "APPROVED"},
    {"name": "Zoom Video Communications", "gst": "27AABCZ1234M1ZX", "status": "APPROVED"},
    # Vendors for specific test scenarios
    {"name": "Suspicious Traders LLC", "gst": None, "status": "BLACKLISTED"},
    {"name": "NewStartup Solutions", "gst": get_random_gst(), "status": "PENDING"},
]

# ────────────────────────────────────────────────────────────
# Core POs — deterministic, match test invoice PO references
# ────────────────────────────────────────────────────────────
CORE_POS = [
    # PO for test 01 (Happy Path AWS) — amount matches invoice total
    {"po_number": "PO-202607-1001", "vendor_name": "AWS India Pvt Ltd", "amount": 1200.0, "status": "OPEN"},
    # PO for test 03 (Bad Tax Microsoft)
    {"po_number": "PO-202607-1002", "vendor_name": "Microsoft Corporation India", "amount": 2500.0, "status": "OPEN"},
    # PO for test 04 (Missing Fields) and test 07 (Split PO - first)
    {"po_number": "PO-202607-1003", "vendor_name": "Google Cloud India", "amount": 5000.0, "status": "OPEN"},
    # PO for test 05 (Math Mismatch)
    {"po_number": "PO-202607-1004", "vendor_name": "Atlassian Pty Ltd", "amount": 5000.0, "status": "OPEN"},
    # PO for test 06 (Stale Invoice)
    {"po_number": "PO-202607-1005", "vendor_name": "Slack Technologies", "amount": 2000.0, "status": "OPEN"},
    # PO for test 07 (Split PO - second)
    {"po_number": "PO-202607-1006", "vendor_name": "Google Cloud India", "amount": 5000.0, "status": "OPEN"},
    # PO for test 08 (Over-Billing) — deliberately small
    {"po_number": "PO-202607-1007", "vendor_name": "Zoom Video Communications", "amount": 5000.0, "status": "OPEN"},
    # A closed PO for testing PO Status rule
    {"po_number": "PO-202607-1008", "vendor_name": "AWS India Pvt Ltd", "amount": 3000.0, "status": "CLOSED"},
    # A cancelled PO
    {"po_number": "PO-202607-1009", "vendor_name": "Microsoft Corporation India", "amount": 1000.0, "status": "CANCELLED"},
]


def seed_vendors(db: Session) -> dict[str, Vendor]:
    """Seed core vendors + some random ones. Returns name→vendor map."""
    print("Seeding vendors...")
    vendor_map = {}
    
    # Core vendors (deterministic)
    for vdata in CORE_VENDORS:
        vendor = Vendor(
            vendor_name=vdata["name"],
            gst_number=vdata["gst"],
            status=vdata["status"],
        )
        db.add(vendor)
        db.flush()
        vendor_map[vdata["name"]] = vendor
    
    # Extra random vendors for realism
    for _ in range(15):
        name = fake.company()
        if name not in vendor_map:
            vendor = Vendor(
                vendor_name=name,
                gst_number=get_random_gst() if random.random() > 0.1 else None,
                status=random.choices(["APPROVED", "PENDING"], weights=[0.85, 0.15])[0],
            )
            db.add(vendor)
            db.flush()
            vendor_map[name] = vendor
    
    db.commit()
    print(f"  → {len(vendor_map)} vendors seeded")
    return vendor_map


def seed_purchase_orders(db: Session, vendor_map: dict[str, Vendor]) -> list[PurchaseOrder]:
    """Seed core POs + some random ones."""
    print("Seeding purchase orders...")
    all_pos = []
    
    # Core POs (deterministic)
    for po_data in CORE_POS:
        vendor = vendor_map.get(po_data["vendor_name"])
        if not vendor:
            print(f"  ⚠ Vendor '{po_data['vendor_name']}' not found, skipping PO {po_data['po_number']}")
            continue
        po = PurchaseOrder(
            po_number=po_data["po_number"],
            vendor_id=vendor.id,
            amount=po_data["amount"],
            currency="INR",
            status=po_data["status"],
        )
        db.add(po)
        all_pos.append(po)
    
    # Extra random POs
    approved_vendors = [v for v in vendor_map.values() if v.status == "APPROVED"]
    for i in range(40):
        vendor = random.choice(approved_vendors)
        amount = round(random.uniform(5000.0, 200000.0), 2)
        po = PurchaseOrder(
            po_number=f"PO-{fake.date_this_year().strftime('%Y%m')}-{random.randint(2000, 9999)}",
            vendor_id=vendor.id,
            amount=amount,
            currency="INR",
            status=random.choices(["OPEN", "CLOSED", "CANCELLED"], weights=[0.7, 0.25, 0.05])[0],
        )
        db.add(po)
        all_pos.append(po)
    
    db.commit()
    print(f"  → {len(all_pos)} purchase orders seeded")
    return all_pos


def seed_demo_invoices(db: Session, vendor_map: dict[str, Vendor], pos: list[PurchaseOrder]):
    """Seed some pre-processed demo invoices with rule results for dashboard history."""
    print("Seeding demo invoices...")
    
    demo_data = [
        {
            "inv_no": "INV/2026/DEMO-001", "vendor": "AWS India Pvt Ltd",
            "subtotal": 15000.0, "tax": 2700.0, "total": 17700.0,
            "status": "APPROVED", "confidence": 0.98, "doc_type": "DIGITAL",
            "explanation": "All validation rules passed. Vendor AWS India Pvt Ltd is approved. Invoice total within PO tolerance. Standard 18% GST applied.",
            "rules": [
                ("Required Fields", "PASS", "All required fields present", "All present"),
                ("Amount Math Validation", "PASS", "17700.0", "17700.0"),
                ("Vendor Matching", "PASS", "AWS India Pvt Ltd", "AWS India Pvt Ltd"),
                ("Tax Rate Validation", "PASS", "Valid GST slab", "18%"),
                ("Duplicate Check", "PASS", "Unique Invoice", "Unique Invoice"),
            ]
        },
        {
            "inv_no": "INV/2026/DEMO-002", "vendor": "Microsoft Corporation India",
            "subtotal": 8500.0, "tax": 1530.0, "total": 10030.0,
            "status": "APPROVED", "confidence": 0.95, "doc_type": "DIGITAL",
            "explanation": "Invoice processed successfully. All 11 validation rules passed. Vendor matched, amounts validated, and PO within tolerance.",
            "rules": [
                ("Required Fields", "PASS", "All required fields present", "All present"),
                ("Amount Math Validation", "PASS", "10030.0", "10030.0"),
                ("Vendor Matching", "PASS", "Microsoft Corporation India", "Microsoft Corporation India"),
                ("Tax Rate Validation", "PASS", "Valid GST slab", "18%"),
                ("Duplicate Check", "PASS", "Unique Invoice", "Unique Invoice"),
            ]
        },
        {
            "inv_no": "INV/2026/DEMO-003", "vendor": "Google Cloud India",
            "subtotal": 22000.0, "tax": 3960.0, "total": 25960.0,
            "status": "PENDING_MANUAL_REVIEW", "confidence": 0.72, "doc_type": "SCANNED",
            "explanation": "Invoice requires manual review. While vendor was matched, the scanned document had moderate OCR confidence (72%). Tax rate appears standard but manual verification is recommended.",
            "rules": [
                ("Required Fields", "PASS", "All required fields present", "All present"),
                ("Amount Math Validation", "PASS", "25960.0", "25960.0"),
                ("Vendor Matching", "PASS", "Google Cloud India", "Google Cloud India"),
                ("Tax Rate Validation", "PASS", "Valid GST slab", "18%"),
                ("Duplicate Check", "PASS", "Unique Invoice", "Unique Invoice"),
                ("PO Amount Tolerance", "FAIL", "≤ ₹21,000.00", "₹25,960.00"),
            ]
        },
        {
            "inv_no": "INV/2026/DEMO-004", "vendor": None,
            "subtotal": 45000.0, "tax": 12600.0, "total": 57600.0,
            "status": "PENDING_MANUAL_REVIEW", "confidence": 0.55, "doc_type": "SCANNED",
            "explanation": "Multiple failures detected. Vendor could not be matched. Anomalous 28% tax rate. Low extraction confidence from scanned document.",
            "rules": [
                ("Required Fields", "FAIL", "All required fields present", "Missing: vendor_name"),
                ("Vendor Matching", "FAIL", "Registered vendor", "Unknown"),
                ("Tax Rate Validation", "PASS", "Valid GST slab", "28%"),
            ]
        },
        {
            "inv_no": "INV/2026/DEMO-005", "vendor": "Atlassian Pty Ltd",
            "subtotal": 6500.0, "tax": 1170.0, "total": 7670.0,
            "status": "REJECTED", "confidence": 0.91, "doc_type": "DIGITAL",
            "explanation": "Invoice REJECTED. Duplicate invoice detected — INV/2026/DEMO-005 has already been submitted and processed for Atlassian Pty Ltd.",
            "rules": [
                ("Required Fields", "PASS", "All required fields present", "All present"),
                ("Duplicate Check", "FAIL", "Unique Invoice", "Duplicate Found"),
            ]
        },
    ]
    
    count = 0
    for d in demo_data:
        vendor = vendor_map.get(d["vendor"]) if d["vendor"] else None
        
        inv = Invoice(
            invoice_number=d["inv_no"],
            vendor_id=vendor.id if vendor else None,
            invoice_date=fake.date_between(start_date="-30d", end_date="today"),
            subtotal=d["subtotal"],
            tax=d["tax"],
            total=d["total"],
            currency="INR",
            status=d["status"],
            document_type=d["doc_type"],
            extraction_confidence=d["confidence"],
            processing_time_ms=random.randint(2000, 8000),
            explanation=d["explanation"],
            file_path=f"uploads/demo_{count + 1}.pdf",
            extracted_data="{}",
        )
        db.add(inv)
        db.flush()
        
        # Add rule results
        for rule_name, result, expected, actual in d.get("rules", []):
            rr = RuleResult(
                invoice_id=inv.id,
                rule_name=rule_name,
                result=result,
                expected=expected,
                actual=actual,
                message=f"{rule_name}: {'Passed' if result == 'PASS' else 'Failed'}",
            )
            db.add(rr)
        
        # Add demo processing logs
        stages = ["File Upload", "Document Detection & OCR", "AI Semantic Extraction",
                   "Context Lookup", "Rule Engine Evaluation", "Decision Engine", "Database Persist"]
        for stage in stages:
            log = ProcessingLog(
                invoice_id=inv.id,
                stage=stage,
                status="COMPLETED",
                duration_ms=random.randint(50, 3000),
            )
            db.add(log)
        
        # Add line items
        num_items = random.randint(1, 4)
        for i in range(num_items):
            item_amount = round(d["subtotal"] / num_items, 2)
            item = InvoiceLineItem(
                invoice_id=inv.id,
                description=fake.catch_phrase(),
                quantity=random.randint(1, 10),
                unit_price=round(item_amount / random.randint(1, 5), 2),
                amount=item_amount,
            )
            db.add(item)
        
        count += 1
    
    # Add some additional random invoices for volume
    approved_vendors = [v for v in vendor_map.values() if v.status == "APPROVED"]
    for _ in range(25):
        vendor = random.choice(approved_vendors)
        subtotal = round(random.uniform(2000.0, 80000.0), 2)
        tax = round(subtotal * random.choice([0.05, 0.12, 0.18, 0.28]), 2)
        total = round(subtotal + tax, 2)
        status = random.choices(["APPROVED", "REJECTED", "PENDING_MANUAL_REVIEW"], weights=[0.6, 0.1, 0.3])[0]
        
        inv = Invoice(
            invoice_number=f"INV/{fake.date_this_year().year}/{random.randint(1000, 9999)}",
            vendor_id=vendor.id,
            invoice_date=fake.date_between(start_date="-60d", end_date="today"),
            subtotal=subtotal,
            tax=tax,
            total=total,
            currency="INR",
            status=status,
            document_type=random.choice(["DIGITAL", "SCANNED"]),
            extraction_confidence=round(random.uniform(0.65, 0.99), 2),
            processing_time_ms=random.randint(1500, 6000),
            explanation=f"{'All rules passed.' if status == 'APPROVED' else 'Review required — rule failures detected.'}",
            file_path=f"uploads/random_{random.randint(1000, 9999)}.pdf",
            extracted_data="{}",
        )
        db.add(inv)
        db.flush()
        
        # Minimal rule results
        for rule_name in ["Required Fields", "Amount Math Validation", "Vendor Matching", "Tax Rate Validation", "Duplicate Check"]:
            result = "PASS" if status == "APPROVED" else random.choice(["PASS", "FAIL"])
            rr = RuleResult(
                invoice_id=inv.id,
                rule_name=rule_name,
                result=result,
                expected="Expected",
                actual="Actual",
                message=f"{rule_name} {'passed' if result == 'PASS' else 'failed'}",
            )
            db.add(rr)
        
        count += 1
    
    db.commit()
    print(f"  → {count} demo invoices seeded (with rule results and processing logs)")


def main():
    db = SessionLocal()
    try:
        from backend.database.base import Base
        from backend.database.session import engine
        Base.metadata.create_all(bind=engine)
        
        # Check if already seeded
        if db.query(Vendor).count() > 0:
            print("Database already contains data. Skipping seed.")
            print("To re-seed, delete financeflow.db and run again.")
            return

        print("=" * 50)
        print("FinanceFlow AI — Database Seed")
        print("=" * 50)
        
        vendor_map = seed_vendors(db)
        pos = seed_purchase_orders(db, vendor_map)
        seed_demo_invoices(db, vendor_map, pos)
        
        print("=" * 50)
        print("✅ Seed completed successfully!")
        print(f"  Vendors: {db.query(Vendor).count()}")
        print(f"  POs: {db.query(PurchaseOrder).count()}")
        print(f"  Invoices: {db.query(Invoice).count()}")
        print(f"  Rule Results: {db.query(RuleResult).count()}")
        print("=" * 50)
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
