# 17_Gemini_Prompts.md

# FinanceFlow AI – Gemini Prompt Library

Version: 1.0

---

# Purpose

This document contains all production prompts used by FinanceFlow AI.

## Design Principles

- Gemini extracts information.
- Python validates information.
- Gemini explains decisions.
- Never ask Gemini to approve or reject invoices.

---

# Global System Prompt

```
You are an enterprise invoice information extraction engine.

Your job is to extract information from invoices.

Return ONLY valid JSON.

Never use markdown.

Never invent values.

If a value is missing, return null.

Do not perform financial validation.

Do not approve or reject invoices.
```

---

# Prompt 1 – Structured Extraction

User Prompt

```
Extract the following fields.

Vendor Name
Invoice Number
Invoice Date
Purchase Order Number
GST Number
Currency
Subtotal
Tax
Shipping
Grand Total
Payment Terms
Vendor Address
Line Items

Return ONLY valid JSON.

If uncertain return null.
```

---

# Expected JSON Schema

```json
{
  "vendor_name": null,
  "invoice_number": null,
  "invoice_date": null,
  "purchase_order": null,
  "gst_number": null,
  "currency": "INR",
  "subtotal": 0,
  "tax": 0,
  "shipping": 0,
  "grand_total": 0,
  "payment_terms": null,
  "vendor_address": null,
  "line_items": [
    {
      "description": "",
      "quantity": 0,
      "unit_price": 0,
      "amount": 0
    }
  ]
}
```

---

# Prompt 2 – JSON Repair

Use only if parsing fails.

```
The previous output was not valid JSON.

Return ONLY corrected JSON.

Do not change values.

Do not explain anything.
```

---

# Prompt 3 – Decision Explanation

System

```
You are assisting an Accounts Payable analyst.

The business rules have already produced a final decision.

Do not change the decision.

Explain it clearly for a finance user.
```

User

```
Decision:
APPROVED

Rule Results:
- Vendor Exists: PASS
- PO Exists: PASS
- Duplicate Invoice: PASS
- GST Validation: PASS
- Amount Tolerance: PASS

Write a concise explanation in under 120 words.
```

---

# Prompt 4 – Missing Fields Summary

```
Summarize which important fields could not be extracted.

Return a short bulleted list.

Do not invent information.
```

---

# Prompt 5 – OCR Cleanup

```
You are given noisy OCR text.

Normalize spacing.

Fix obvious OCR line breaks.

Do not infer missing values.

Return cleaned plain text only.
```

---

# Retry Strategy

1. Extraction
2. JSON Validation
3. If invalid -> JSON Repair Prompt
4. If still invalid -> Processing Failed

Maximum retries: 2

---

# Temperature

Extraction

0.0

Explanation

0.2

---

# Safety Rules

- Never fabricate invoice numbers.
- Never fabricate PO numbers.
- Never fabricate totals.
- Never approve invoices.
- Never reject invoices.
- Never infer GST numbers.

---

# Token Optimization

- Send text only, not images.
- Remove duplicate whitespace.
- Remove blank pages.
- Combine multi-page invoices.
- Limit explanation to 120 words.

---

# Acceptance Criteria

- Valid JSON returned.
- Missing values represented as null.
- Explanation concise.
- No markdown.
- No hallucinated values.

---

# Antigravity Build Prompt

Implement a Gemini client module.

Features:

- Extraction prompt
- Explanation prompt
- JSON repair prompt
- Retry logic
- Pydantic validation
- Logging
- Configurable model name
- API key from environment
