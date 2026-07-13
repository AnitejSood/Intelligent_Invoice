# 18_Antigravity_Build_Prompts.md

# FinanceFlow AI – Antigravity Build Prompts

Version: 1.0

---

# Purpose

This document contains phased implementation prompts for Antigravity. Execute one prompt at a time. Do not combine phases. Ensure the project compiles and passes basic verification before moving to the next phase.

---

# Phase 1 – Scaffold Repository

## Goal

Initialize the complete project skeleton.

### Prompt

```
Create a production-ready monorepo for FinanceFlow AI.

Generate:

- backend (FastAPI)
- frontend (React + Vite + TypeScript)
- docs
- sample_data
- scripts

Configure:

- TailwindCSS
- shadcn/ui
- React Query
- React Router
- SQLAlchemy
- Alembic
- Ruff
- Black
- Prettier
- ESLint

Create placeholder modules only.

The project must build successfully without business logic.
```

Acceptance:

- Backend starts.
- Frontend starts.
- No TypeScript errors.
- No Python import errors.

---

# Phase 2 – Database

## Goal

Create all database models.

### Prompt

```
Implement SQLAlchemy models using the documentation.

Generate:

Vendor
PurchaseOrder
Invoice
LineItem
RuleResult
ProcessingLog

Create Alembic migration.

Generate Faker seed script.

Do not implement APIs yet.
```

Acceptance

- Migration succeeds.
- Database seeds successfully.

---

# Phase 3 – Backend APIs

## Prompt

```
Create FastAPI routers.

Generate:

/health
/dashboard
/invoices
/history

Use APIRouter.

Use repository pattern.

Use dependency injection.

Implement OpenAPI documentation.
```

Acceptance

- Swagger loads.
- Endpoints return mock responses.

---

# Phase 4 – OCR

## Prompt

```
Implement document detection.

If PDF contains embedded text

Use PyMuPDF.

Else

Run PaddleOCR.

Return:

document_type

text

confidence

processing_time

Log every stage.
```

Acceptance

- Digital PDF works.
- Scanned PDF works.

---

# Phase 5 – Gemini

## Prompt

```
Implement Gemini client.

Use prompts defined in 17_Gemini_Prompts.md.

Features

Structured extraction

JSON validation

Retry once

Decision explanation

Environment variables

Logging

Do not implement approval logic.
```

Acceptance

- Valid JSON returned.
- Retry works.

---

# Phase 6 – Rule Engine

## Prompt

```
Implement deterministic validation.

Rules

Vendor

PO

GST

Duplicate

Amount

Date

Confidence

Required Fields

Generate:

RuleResult objects

Final Decision

Audit log
```

Acceptance

- Same input always produces same decision.

---

# Phase 7 – Dashboard

## Prompt

```
Build dashboard.

Cards

Approved

Rejected

Pending

Processing Time

Approval Rate

Charts

Recent invoices

Responsive design.

Use shadcn/ui.
```

Acceptance

- Dashboard responsive.
- Loads from API.

---

# Phase 8 – Upload

## Prompt

```
Create upload page.

Drag and Drop

Progress

Validation

Toast notifications

Trigger backend upload.

Display processing timeline.
```

Acceptance

- Upload succeeds.
- Timeline updates.

---

# Phase 9 – Invoice Details

## Prompt

```
Create invoice details page.

Split layout.

PDF preview.

Extracted fields.

Rule results.

Decision card.

AI explanation.

Timeline.
```

Acceptance

- Details render correctly.

---

# Phase 10 – History

## Prompt

```
Create searchable history page.

Search

Status filter

Document type filter

Pagination

Click row to details.
```

Acceptance

- History searchable.

---

# Phase 11 – Polish

## Prompt

```
Improve UI.

Skeletons

Loading

Error states

Responsive

Animations

Dark mode support

Accessibility improvements
```

Acceptance

- Lighthouse accessibility >90.
- No layout shifts.

---

# Phase 12 – Deployment

## Prompt

```
Prepare deployment.

Frontend

Vercel

Backend

Render

Create .env.example

Update README

Verify production build.
```

Acceptance

- Production deployment succeeds.

---

# Global Rules

- Never put business rules in React.
- Never let Gemini approve invoices.
- Keep services modular.
- Prefer reusable components.
- Use strict typing.
- Handle all errors gracefully.
- Add logging for every major step.

---

# Completion Checklist

- Backend operational
- Frontend operational
- OCR working
- Gemini integrated
- Rule engine working
- Dashboard complete
- History complete
- Deployment complete
- Demo ready
