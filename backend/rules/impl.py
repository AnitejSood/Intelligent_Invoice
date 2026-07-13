"""Implementation of business rules."""

from datetime import datetime, date
from typing import Any

from backend.models.rule_result import RuleResult
from backend.rules.base_rule import BaseRule
from backend.llm.gemini_client import ExtractedInvoiceData
from backend.core.config import settings


class RequiredFieldsRule(BaseRule):
    @property
    def name(self) -> str:
        return "Required Fields"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        from backend.services.settings_service import SettingsService
        rule_settings = SettingsService.get_all()
        require_po = rule_settings.get("REQUIRE_PO", True)

        missing = []
        if not data.invoice_number: missing.append("invoice_number")
        if not data.vendor_name: missing.append("vendor_name")
        if not data.invoice_date: missing.append("invoice_date")
        if not data.total and data.total != 0: missing.append("total")
        
        if require_po and not data.po_number:
            missing.append("po_number")
            
        if missing:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="All required fields present",
                actual=f"Missing: {', '.join(missing)}",
                message=f"Mandatory fields are missing from extraction: {', '.join(missing)}"
            )
            
        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected="All required fields present",
            actual="All present",
            message="All required fields extracted successfully"
        )


class AmountMathRule(BaseRule):
    @property
    def name(self) -> str:
        return "Amount Math Validation"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        expected_total = round(data.subtotal + data.tax + data.shipping, 2)
        actual_total = round(data.total, 2)
        difference = abs(expected_total - actual_total)
        
        # Allow ±₹1 rounding tolerance
        if difference <= 1.0:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected=str(expected_total),
                actual=str(actual_total),
                message=f"Subtotal + Tax + Shipping matches Total (diff: ₹{difference:.2f})"
            )
        else:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected=str(expected_total),
                actual=str(actual_total),
                message=f"Math mismatch in totals. Computed ₹{expected_total} but invoice shows ₹{actual_total} (₹{difference:.2f} discrepancy)"
            )


class VendorMatchRule(BaseRule):
    @property
    def name(self) -> str:
        return "Vendor Matching"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        vendor = context.get("vendor")
        if vendor:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="Registered vendor",
                actual=vendor.vendor_name,
                message=f"Vendor '{data.vendor_name}' matched to registered entity '{vendor.vendor_name}'"
            )
        else:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="Registered vendor in database",
                actual=data.vendor_name or "Unknown",
                message=f"Vendor '{data.vendor_name or 'Unknown'}' not found in approved vendor registry"
            )


class VendorStatusRule(BaseRule):
    """Check if the matched vendor is in good standing (not BLACKLISTED or PENDING)."""
    @property
    def name(self) -> str:
        return "Vendor Status Check"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        vendor = context.get("vendor")
        if not vendor:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual="No vendor matched",
                message="Vendor status not applicable — vendor not in database"
            )
        
        if vendor.status == "APPROVED":
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="APPROVED",
                actual=vendor.status,
                message=f"Vendor '{vendor.vendor_name}' is in APPROVED status"
            )
        else:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="APPROVED",
                actual=vendor.status,
                message=f"Vendor '{vendor.vendor_name}' has status '{vendor.status}' — invoices from non-approved vendors require escalation"
            )


class DuplicateInvoiceRule(BaseRule):
    @property
    def name(self) -> str:
        return "Duplicate Check"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        is_duplicate = context.get("is_duplicate", False)
        if is_duplicate:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="Unique Invoice",
                actual="Duplicate Found",
                message=f"Invoice {data.invoice_number} has already been processed for this vendor"
            )
        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected="Unique Invoice",
            actual="Unique Invoice",
            message="No duplicate found in the system"
        )


class TaxRateRule(BaseRule):
    @property
    def name(self) -> str:
        return "Tax Rate Validation"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        if data.subtotal == 0:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual="No Subtotal",
                message="Subtotal is zero, skipping tax rate check"
            )
            
        tax_percentage = round((data.tax / data.subtotal) * 100)
        # Acceptable Indian GST tax brackets: 0%, 5%, 12%, 18%, 28%
        valid_rates = [0, 5, 12, 18, 28]
        
        if tax_percentage in valid_rates:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="Valid GST slab (0/5/12/18/28%)",
                actual=f"{tax_percentage}%",
                message=f"Tax rate {tax_percentage}% matches standard GST slab"
            )
        else:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="0%, 5%, 12%, 18%, or 28%",
                actual=f"{tax_percentage}%",
                message=f"Tax rate of {tax_percentage}% does not match any standard GST slab. Possible miscalculation or non-standard rate."
            )


class POToleranceRule(BaseRule):
    @property
    def name(self) -> str:
        return "PO Amount Tolerance"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        from backend.services.settings_service import SettingsService
        rule_settings = SettingsService.get_all()
        tolerance_percent = rule_settings.get("PO_TOLERANCE_PERCENT", 5.0)
        
        pos = context.get("matched_pos", [])
        po = context.get("po")
        
        # If multi-PO, sum amounts
        if pos:
            po_amount = sum(float(p.amount) for p in pos)
            po_label = f"{len(pos)} linked POs"
        elif po:
            po_amount = float(po.amount)
            po_label = f"PO {po.po_number}"
        else:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="No PO referenced",
                actual="N/A",
                message="No PO validation required (no PO matched)"
            )
            
        invoice_total = float(data.total)
        allowed_max = po_amount * (1 + tolerance_percent / 100.0)
        
        if invoice_total > allowed_max:
            overage = invoice_total - po_amount
            overage_pct = (overage / po_amount * 100) if po_amount > 0 else 0
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected=f"≤ ₹{allowed_max:,.2f} ({po_label}: ₹{po_amount:,.2f} + {tolerance_percent}%)",
                actual=f"₹{invoice_total:,.2f} (+{overage_pct:.1f}% over)",
                message=f"Invoice total ₹{invoice_total:,.2f} exceeds {po_label} amount ₹{po_amount:,.2f} by ₹{overage:,.2f} ({overage_pct:.1f}%), which is beyond the {tolerance_percent}% tolerance"
            )
            
        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected=f"≤ ₹{allowed_max:,.2f} ({po_label}: ₹{po_amount:,.2f} + {tolerance_percent}%)",
            actual=f"₹{invoice_total:,.2f}",
            message=f"Invoice amount ₹{invoice_total:,.2f} is within the {po_label} tolerance limit of ₹{allowed_max:,.2f}"
        )


class POStatusRule(BaseRule):
    """Verify that matched PO(s) are in OPEN status, not CLOSED or CANCELLED."""
    @property
    def name(self) -> str:
        return "PO Status Check"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        pos = context.get("matched_pos", [])
        po = context.get("po")
        
        check_list = pos if pos else ([po] if po else [])
        
        if not check_list:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual="No PO referenced",
                message="PO status check not applicable — no PO linked"
            )
        
        bad_pos = [p for p in check_list if p.status != "OPEN"]
        if bad_pos:
            bad_details = ", ".join(f"{p.po_number} ({p.status})" for p in bad_pos)
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected="All POs in OPEN status",
                actual=bad_details,
                message=f"Cannot bill against non-OPEN purchase orders: {bad_details}"
            )
        
        po_list = ", ".join(p.po_number for p in check_list)
        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected="All POs in OPEN status",
            actual=f"OPEN ({po_list})",
            message=f"All linked purchase orders are in OPEN status"
        )


class InvoiceAgeRule(BaseRule):
    """Reject invoices that are older than the configured MAX_INVOICE_AGE_DAYS."""
    @property
    def name(self) -> str:
        return "Invoice Freshness"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        from backend.services.settings_service import SettingsService
        rule_settings = SettingsService.get_all()
        max_age_days = rule_settings.get("MAX_INVOICE_AGE_DAYS", 365)

        if not data.invoice_date:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual="No date available",
                message="Invoice date not extracted — age check skipped"
            )

        try:
            inv_date = datetime.strptime(data.invoice_date, "%Y-%m-%d").date()
        except ValueError:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual=data.invoice_date,
                message="Could not parse invoice date — age check skipped"
            )

        age_days = (date.today() - inv_date).days
        
        if age_days > max_age_days:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected=f"≤ {max_age_days} days old",
                actual=f"{age_days} days old",
                message=f"Invoice dated {data.invoice_date} is {age_days} days old, exceeding the {max_age_days}-day limit. Stale invoices require management approval."
            )

        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected=f"≤ {max_age_days} days old",
            actual=f"{age_days} days old",
            message=f"Invoice is {age_days} days old, within the acceptable window"
        )


class LineItemsIntegrityRule(BaseRule):
    """Verify that line item amounts sum to the subtotal."""
    @property
    def name(self) -> str:
        return "Line Items Integrity"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        if not data.line_items:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual="No line items extracted",
                message="No line items to validate — check skipped"
            )

        items_total = round(sum(item.amount for item in data.line_items), 2)
        subtotal = round(data.subtotal, 2)
        diff = abs(items_total - subtotal)

        if diff <= 1.0:  # Allow ₹1 rounding tolerance
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected=f"₹{subtotal:,.2f}",
                actual=f"₹{items_total:,.2f} ({len(data.line_items)} items)",
                message=f"Line items sum ₹{items_total:,.2f} matches subtotal ₹{subtotal:,.2f}"
            )
        else:
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected=f"₹{subtotal:,.2f}",
                actual=f"₹{items_total:,.2f} ({len(data.line_items)} items)",
                message=f"Line items sum ₹{items_total:,.2f} does not match subtotal ₹{subtotal:,.2f} — ₹{diff:,.2f} discrepancy"
            )


class CurrencyConsistencyRule(BaseRule):
    """Flag currency mismatches between invoice and PO."""
    @property
    def name(self) -> str:
        return "Currency Consistency"

    def evaluate(self, data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        po = context.get("po")
        pos = context.get("matched_pos", [])
        check_list = pos if pos else ([po] if po else [])

        if not check_list:
            return RuleResult(
                rule_name=self.name,
                result="PASS",
                expected="N/A",
                actual=data.currency,
                message="No PO to compare currency against"
            )

        mismatched = [p for p in check_list if p.currency != data.currency]
        if mismatched:
            mismatch_info = ", ".join(f"{p.po_number}: {p.currency}" for p in mismatched)
            return RuleResult(
                rule_name=self.name,
                result="FAIL",
                expected=f"Invoice currency ({data.currency})",
                actual=mismatch_info,
                message=f"Currency mismatch: Invoice in {data.currency} but PO(s) in different currencies: {mismatch_info}"
            )

        return RuleResult(
            rule_name=self.name,
            result="PASS",
            expected=data.currency,
            actual=data.currency,
            message=f"Invoice and PO currencies match ({data.currency})"
        )


# List of all active rules — ordered by evaluation priority
ACTIVE_RULES = [
    RequiredFieldsRule(),
    AmountMathRule(),
    LineItemsIntegrityRule(),
    TaxRateRule(),
    VendorMatchRule(),
    VendorStatusRule(),
    DuplicateInvoiceRule(),
    InvoiceAgeRule(),
    POToleranceRule(),
    POStatusRule(),
    CurrencyConsistencyRule(),
]
