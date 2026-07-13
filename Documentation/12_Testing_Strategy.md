# 12_Testing_Strategy.md

# FinanceFlow AI – Testing Strategy

Version: 1.0

---

# Purpose

This document defines the testing approach for FinanceFlow AI. The objective is to ensure the complete invoice processing workflow is reliable before the interview demo.

---

# Testing Pyramid

```text
            UI Tests
        Integration Tests
            Unit Tests
```

Focus primarily on unit and integration testing for the MVP.

---

# Test Categories

## Unit Tests

Test individual services independently.

Services:

- document_service
- ocr_service
- gemini_service (mocked)
- validation_service
- decision_service

---

## Integration Tests

Verify complete pipeline.

Example

Upload PDF

↓

Extract Text

↓

Gemini JSON

↓

Rule Engine

↓

Database

↓

Dashboard

---

## UI Tests

Verify

- Upload page
- Dashboard
- Invoice Details
- History
- Timeline

---

# Happy Path

Expected Result

- Upload succeeds
- Invoice extracted
- Rules pass
- Decision APPROVED
- History updated

---

# Edge Cases

## Duplicate Invoice

Expected

REJECTED

---

## Missing Purchase Order

Expected

PENDING_MANUAL_REVIEW

---

## Low OCR Confidence

Expected

PENDING_MANUAL_REVIEW

---

## Invalid GST

Expected

PENDING_MANUAL_REVIEW

---

## Corrupted PDF

Expected

Upload rejected gracefully

---

# Manual Test Checklist

| Test | Expected |
|------|----------|
| Upload digital PDF | Success |
| Upload scanned PDF | Success |
| Dashboard refresh | Updated metrics |
| Search history | Correct results |
| Invoice details | All sections visible |
| Timeline | Complete stages shown |

---

# API Tests

Health endpoint

Dashboard endpoint

Upload endpoint

History endpoint

Invoice details endpoint

Reprocess endpoint

Expected

- 200 success
- Correct JSON schema
- Consistent error format

---

# Database Validation

Verify

- Invoice saved
- Rule results persisted
- Processing logs created
- No duplicate history rows

---

# Performance Targets

| Metric | Target |
|---------|--------|
| Upload response | < 1 s (acceptance) |
| End-to-end processing | < 6 s |
| Dashboard load | < 2 s |

---

# Demo Regression Checklist

Before recording demo:

- Restart backend
- Restart frontend
- Seed database
- Test one digital invoice
- Test one scanned invoice
- Test duplicate invoice
- Test missing PO
- Verify deployment URLs

---

# Known MVP Limitations

- SQLite only
- Single-user
- No authentication
- English invoices
- Local file storage

Be prepared to mention these in the interview.

---

# Acceptance Criteria

- Happy path passes
- All edge cases behave correctly
- No unhandled exceptions
- Consistent API responses
- UI remains responsive

---

# Antigravity Build Prompt

Create automated tests using pytest for backend services and React Testing Library for critical frontend components.

Mock Gemini responses.

Include fixtures for:

- Digital invoice
- Scanned invoice
- Duplicate invoice
- Missing PO
- Invalid GST

Ensure tests can run locally with a single command.
