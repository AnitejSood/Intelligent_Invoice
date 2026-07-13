# 02_System_Architecture.md

# FinanceFlow AI – System Architecture

Version: 1.0

---

# Purpose

This document defines the technical architecture of FinanceFlow AI. The system is designed using a hybrid AI approach where AI performs semantic extraction and explanation, while deterministic Python code performs all financial validation and approval decisions.

---

# Architecture Principles

1. AI assists, never decides.
2. Every decision is explainable.
3. Every processing step is observable.
4. Business rules are deterministic.
5. Services are modular.
6. Optimize LLM usage.

---

# High-Level Architecture

```mermaid
flowchart TD

U[React Frontend]

API[FastAPI]

DOC[Document Service]

OCR[OCR Service]

LLM[Gemini Service]

RULES[Rule Engine]

DB[(SQLite)]

UI[Dashboard]

U-->API
API-->DOC
DOC-->OCR
OCR-->LLM
LLM-->RULES
RULES-->DB
DB-->UI
UI-->U
```

---

# Processing Pipeline

```mermaid
flowchart LR

A[Upload Invoice]

B[Detect PDF Type]

C1[Digital PDF]

C2[Scanned PDF]

D1[PyMuPDF]

D2[PaddleOCR]

E[Clean Text]

F[Gemini Extraction]

G[Business Rule Engine]

H[Decision]

I[Gemini Explanation]

J[(SQLite)]

K[Dashboard]

A-->B
B-->C1
B-->C2
C1-->D1
C2-->D2
D1-->E
D2-->E
E-->F
F-->G
G-->H
H-->I
I-->J
J-->K
```

---

# Service Responsibilities

## Frontend

Responsible for:

- Upload UI
- Dashboard
- Invoice History
- Processing Timeline
- Invoice Details
- Error Handling

No business logic.

---

## FastAPI

Responsible for:

- API routing
- Validation
- Service orchestration
- File management
- Exception handling

---

## Document Service

Responsibilities

- Save upload
- Detect PDF type
- Route to extraction pipeline

Outputs

- Document metadata
- Processing job

---

## OCR Service

Digital PDFs

- PyMuPDF
- pdfplumber fallback

Scanned PDFs

- PaddleOCR

Outputs

- Plain text
- OCR confidence

---

## Gemini Service

Responsibilities

- Extract structured JSON
- Generate explanation

Never decides approval.

---

## Rule Engine

Checks

- Vendor exists
- Purchase Order exists
- Duplicate invoice
- GST validity
- Currency
- Date
- Amount tolerance
- Required fields

Outputs

- PASS/FAIL per rule
- Final status

---

## Decision Engine

Possible decisions

- APPROVED
- REJECTED
- PENDING MANUAL REVIEW

---

## History Service

Stores

- Extracted JSON
- Rule evaluation
- Timeline
- Decision
- Explanation
- Processing time

---

# Request Lifecycle

1. User uploads invoice.
2. Backend stores file.
3. Detect digital vs scanned.
4. Extract text.
5. Normalize text.
6. Gemini converts text to JSON.
7. Rule engine validates.
8. Decision generated.
9. Gemini writes explanation.
10. Results stored.
11. Dashboard updated.

---

# Error Recovery

| Failure | Recovery |
|---------|----------|
| OCR fails | Manual Review |
| Gemini timeout | Retry once |
| Invalid JSON | Retry with stricter prompt |
| Corrupted PDF | Reject upload |
| Missing PO | Pending Review |

---

# Security

- Gemini API key stored in environment variables.
- Validate MIME type before processing.
- Limit upload size.
- Store only metadata required for history.
- Sanitize filenames.

---

# Scalability

Current

React → FastAPI → SQLite

Future

React

↓

FastAPI

↓

Redis Queue

↓

Celery Workers

↓

PostgreSQL

↓

S3 Storage

↓

SAP / Oracle ERP Integrations

---

# Acceptance Criteria

- Modular services.
- Automatic document detection.
- Hybrid OCR pipeline.
- Gemini used only for extraction/explanation.
- Rule engine independent of AI.
- Complete processing history.
- Dashboard reflects latest state.

---

# Antigravity Build Prompt

Build the backend architecture exactly as specified.

Create independent services:

- document_service.py
- ocr_service.py
- gemini_service.py
- validation_service.py
- decision_service.py
- history_service.py

Use dependency injection where practical.

No business rules should exist inside React components or Gemini prompts.

Maintain clean architecture with reusable services and typed models.
