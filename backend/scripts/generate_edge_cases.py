"""Generate synthetic test invoices for edge case demonstration.

Creates 8 diverse test PDFs covering every edge case scenario.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUTPUT_DIR = "test_invoices"


def create_invoice(file_name, vendor, po, invoice_no, date_str, subtotal, tax, total,
                   shipping=0.0, currency="INR", gst=None, line_items=None,
                   is_scanned=False, extra_po=None, omit_fields=None):
    """Generate a test invoice PDF with configurable fields."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, file_name)
    omit = omit_fields or []
    
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 50
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, y, "INVOICE")
    y -= 10
    
    # Thin colored line
    c.setStrokeColor(colors.HexColor("#6C3BF5"))
    c.setLineWidth(2)
    c.line(50, y, width - 50, y)
    y -= 30
    
    # Two-column layout
    c.setFont("Helvetica", 11)
    
    if "vendor_name" not in omit:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "VENDOR:")
        c.setFont("Helvetica", 11)
        c.drawString(110, y, vendor)
        y -= 20
    
    if gst and "gst" not in omit:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "GSTIN:")
        c.setFont("Helvetica", 11)
        c.drawString(110, y, gst)
        y -= 20
    
    right_x = width - 250
    right_y = height - 90
    
    if "invoice_no" not in omit:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(right_x, right_y, "INVOICE NO:")
        c.setFont("Helvetica", 11)
        c.drawString(right_x + 80, right_y, invoice_no)
        right_y -= 20
    
    if "date" not in omit:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(right_x, right_y, "DATE:")
        c.setFont("Helvetica", 11)
        c.drawString(right_x + 80, right_y, date_str)
        right_y -= 20
    
    if "po" not in omit:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(right_x, right_y, "PO REF:")
        c.setFont("Helvetica", 11)
        po_text = po
        if extra_po:
            po_text = f"{po}, {extra_po}"
        c.drawString(right_x + 80, right_y, po_text)
        right_y -= 20
    
    c.setFont("Helvetica", 11)
    c.drawString(right_x, right_y, f"Currency: {currency}")
    
    y = min(y, right_y) - 20
    
    # Table Header
    c.setStrokeColor(colors.black)
    c.line(50, y, width - 50, y)
    y -= 18
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(300, y, "Qty")
    c.drawString(380, y, "Unit Price")
    c.drawString(480, y, "Amount")
    y -= 5
    c.setStrokeColor(colors.grey)
    c.line(50, y, width - 50, y)
    y -= 18
    
    # Line Items
    c.setFont("Helvetica", 10)
    items = line_items or [{"desc": "Software License Subscription", "qty": 1, "price": subtotal, "amount": subtotal}]
    
    for item in items:
        c.drawString(50, y, str(item["desc"]))
        c.drawString(300, y, str(item["qty"]))
        c.drawString(380, y, f"{item['price']:,.2f}")
        c.drawString(480, y, f"{item['amount']:,.2f}")
        y -= 18
    
    y -= 5
    c.line(50, y, width - 50, y)
    y -= 25
    
    # Totals
    c.setFont("Helvetica", 11)
    c.drawString(380, y, "Subtotal:")
    c.drawRightString(width - 60, y, f"{currency} {subtotal:,.2f}")
    y -= 18
    
    c.drawString(380, y, "Tax (GST):")
    c.drawRightString(width - 60, y, f"{currency} {tax:,.2f}")
    y -= 18
    
    if shipping > 0:
        c.drawString(380, y, "Shipping:")
        c.drawRightString(width - 60, y, f"{currency} {shipping:,.2f}")
        y -= 18
    
    c.setStrokeColor(colors.black)
    c.line(380, y, width - 50, y)
    y -= 20
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(380, y, "TOTAL:")
    c.drawRightString(width - 60, y, f"{currency} {total:,.2f}")
    
    if is_scanned:
        # Simulate scan noise artifacts
        c.setStrokeColor(colors.lightgrey)
        c.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))
        for i in range(0, int(width), 15):
            for j in range(0, int(height), 15):
                if (i + j) % 30 == 0:
                    c.circle(i, j, 0.4, fill=1)
                    
    c.save()
    print(f"Generated: {path}")


def generate_all():
    """Generate all 8 edge case test invoices."""
    
    # ──────────────────────────────────────────────────
    # 1. Happy Path — Clean digital, all fields, valid PO, 18% GST
    #    Expected: ✅ APPROVED
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="01_Happy_Path_AWS.pdf",
        vendor="AWS India Pvt Ltd",
        po="PO-202607-1001",
        invoice_no="INV-AWS-8899",
        date_str="2026-07-10",
        subtotal=1000.0,
        tax=180.0,  # 18% GST
        total=1180.0,
        gst="29AABCU9603R1ZM",
        line_items=[
            {"desc": "EC2 Reserved Instances (12mo)", "qty": 2, "price": 300.00, "amount": 600.00},
            {"desc": "S3 Storage (500GB)", "qty": 1, "price": 250.00, "amount": 250.00},
            {"desc": "CloudWatch Monitoring", "qty": 1, "price": 150.00, "amount": 150.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 2. Ghost Vendor — Unknown vendor not in approved vendor list
    #    Expected: ⚠️ PENDING (Vendor Match FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="02_Ghost_Vendor_Acme.pdf",
        vendor="Acme Corp International",
        po="PO-999999",
        invoice_no="INV-ACME-001",
        date_str="2026-07-11",
        subtotal=5000.0,
        tax=900.0,  # 18%
        total=5900.0,
        is_scanned=True,
        line_items=[
            {"desc": "Office Supplies Bulk Order", "qty": 50, "price": 100.00, "amount": 5000.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 3. Anomalous Tax Rate — 23% GST (not a valid slab)
    #    Expected: ⚠️ PENDING (Tax Rate FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="03_Bad_Tax_Microsoft.pdf",
        vendor="Microsoft Corporation India",
        po="PO-202607-1002",
        invoice_no="INV-MS-4455",
        date_str="2026-07-11",
        subtotal=2000.0,
        tax=460.0,  # 23% — anomalous
        total=2460.0,
        gst="27AABCM1234F1ZP",
        line_items=[
            {"desc": "Azure VM (Standard D4s v3)", "qty": 1, "price": 1200.00, "amount": 1200.00},
            {"desc": "Microsoft 365 E5 License", "qty": 4, "price": 200.00, "amount": 800.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 4. Missing Fields — No invoice number, no date
    #    Expected: ⚠️ PENDING (Required Fields FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="04_Missing_Fields.pdf",
        vendor="Google Cloud India",
        po="PO-202607-1003",
        invoice_no="",  # Missing
        date_str="",    # Missing
        subtotal=3500.0,
        tax=630.0,  # 18%
        total=4130.0,
        omit_fields=["invoice_no", "date"],
        line_items=[
            {"desc": "BigQuery Analysis (TB)", "qty": 10, "price": 200.00, "amount": 2000.00},
            {"desc": "Cloud Functions Invocations", "qty": 1, "price": 1500.00, "amount": 1500.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 5. Math Mismatch — Subtotal + Tax ≠ Total
    #    Expected: ⚠️ PENDING (Amount Math FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="05_Math_Mismatch.pdf",
        vendor="Atlassian Pty Ltd",
        po="PO-202607-1004",
        invoice_no="INV-ATL-7722",
        date_str="2026-07-08",
        subtotal=4000.0,
        tax=720.0,       # 18%
        total=5200.0,     # Should be 4720 — ₹480 discrepancy
        gst="06AABCA5678Q1ZN",
        line_items=[
            {"desc": "Jira Software (100 users)", "qty": 1, "price": 2500.00, "amount": 2500.00},
            {"desc": "Confluence (100 users)", "qty": 1, "price": 1500.00, "amount": 1500.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 6. Stale Invoice — Invoice dated 2 years ago
    #    Expected: ⚠️ PENDING (Invoice Age FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="06_Stale_Invoice.pdf",
        vendor="Slack Technologies",
        po="PO-202607-1005",
        invoice_no="INV-SLACK-2024-001",
        date_str="2024-03-15",  # Over 2 years old
        subtotal=1500.0,
        tax=270.0,  # 18%
        total=1770.0,
        line_items=[
            {"desc": "Slack Pro Plan (Annual)", "qty": 50, "price": 30.00, "amount": 1500.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 7. Split PO — References two PO numbers
    #    Expected: ✅ APPROVED (Multi-PO linked)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="07_Split_PO_Google.pdf",
        vendor="Google Cloud India",
        po="PO-202607-1003",
        extra_po="PO-202607-1006",
        invoice_no="INV-GCP-5566",
        date_str="2026-07-09",
        subtotal=8000.0,
        tax=1440.0,  # 18%
        total=9440.0,
        gst="29AABCG7890R1ZK",
        line_items=[
            {"desc": "GKE Cluster (Autopilot)", "qty": 1, "price": 3000.00, "amount": 3000.00},
            {"desc": "Cloud SQL Enterprise", "qty": 2, "price": 1500.00, "amount": 3000.00},
            {"desc": "Cloud CDN Traffic (TB)", "qty": 20, "price": 100.00, "amount": 2000.00},
        ]
    )
    
    # ──────────────────────────────────────────────────
    # 8. Over-Billing — Invoice 20% over PO amount
    #    Expected: ⚠️ PENDING (PO Tolerance FAIL)
    # ──────────────────────────────────────────────────
    create_invoice(
        file_name="08_Over_Billing.pdf",
        vendor="Zoom Video Communications",
        po="PO-202607-1007",
        invoice_no="INV-ZOOM-3344",
        date_str="2026-07-12",
        subtotal=6000.0,
        tax=1080.0,  # 18%
        total=7080.0,  # PO is only for 5000 → 41.6% over
        gst="27AABCZ1234M1ZX",
        line_items=[
            {"desc": "Zoom Enterprise License", "qty": 200, "price": 20.00, "amount": 4000.00},
            {"desc": "Zoom Rooms Hardware", "qty": 10, "price": 200.00, "amount": 2000.00},
        ]
    )

    print(f"\n✅ Generated 8 test invoices in '{OUTPUT_DIR}/' directory")
    print("Scenarios covered:")
    print("  01: Happy Path (APPROVED)")
    print("  02: Ghost Vendor (Vendor Match FAIL)")
    print("  03: Bad Tax Rate (Tax Rate FAIL)")
    print("  04: Missing Fields (Required Fields FAIL)")
    print("  05: Math Mismatch (Amount Math FAIL)")
    print("  06: Stale Invoice (Invoice Age FAIL)")
    print("  07: Split PO (Multi-PO linking)")
    print("  08: Over-Billing (PO Tolerance FAIL)")


if __name__ == "__main__":
    generate_all()
