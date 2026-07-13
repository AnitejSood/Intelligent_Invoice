# 06_API_Specification.md

# FinanceFlow AI – API Specification

Version: 1.0

---

# Purpose

This document defines the REST API exposed by the FastAPI backend. All endpoints return JSON and follow a consistent response contract.

Base URL

```
/api/v1
```

Content Type

```
application/json
```

Authentication

Not required for MVP. Future versions may use JWT.

---

# Standard Response Format

## Success

```json
{
  "success": true,
  "message": "Invoice processed successfully",
  "data": {}
}
```

## Error

```json
{
  "success": false,
  "message": "Purchase Order not found",
  "code": "PO_NOT_FOUND"
}
```

---

# Endpoints

## Health

### GET /health

Returns service status.

Response

```json
{
  "status":"healthy",
  "version":"1.0.0"
}
```

---

## Upload Invoice

### POST /invoices/upload

Content-Type

multipart/form-data

Body

| Field | Type |
|------|------|
| file | PDF |

Flow

1. Save upload
2. Detect document type
3. Extract text
4. Gemini extraction
5. Rule validation
6. Decision
7. Persist results

Response

```json
{
  "invoice_id":12,
  "status":"APPROVED"
}
```

---

## Get Invoice

### GET /invoices/{invoice_id}

Returns

- Metadata
- Extracted fields
- Rule results
- Timeline
- Explanation

---

## Reprocess Invoice

### POST /invoices/{invoice_id}/reprocess

Re-runs OCR, extraction and validation using current rules.

---

## Invoice History

### GET /invoices

Query Parameters

| Parameter | Description |
|------------|-------------|
| page | Pagination |
| limit | Page size |
| search | Invoice/vendor |
| status | Approved/Rejected/Pending |
| type | Digital/Scanned |

Response

```json
{
  "items":[],
  "total":100,
  "page":1
}
```

---

## Dashboard

### GET /dashboard

Returns

- Total invoices
- Approved
- Rejected
- Pending
- Avg processing time
- Approval rate
- Recent invoices

---

## Dashboard Analytics

### GET /dashboard/analytics

Returns chart-ready datasets.

Example

```json
{
  "approval_rate":91,
  "processing_trend":[],
  "invoice_types":[]
}
```

---

## Vendors

### GET /vendors

Returns approved vendors.

### GET /vendors/{vendor_id}

Vendor details.

Future

POST /vendors

PUT /vendors/{id}

DELETE /vendors/{id}

---

## Purchase Orders

### GET /purchase-orders

Supports pagination and search.

---

# Error Codes

| Code | Meaning |
|------|---------|
| INVALID_FILE | Unsupported upload |
| OCR_FAILED | OCR error |
| GEMINI_TIMEOUT | AI timeout |
| INVALID_JSON | Extraction failed |
| DUPLICATE_INVOICE | Duplicate detected |
| PO_NOT_FOUND | Missing PO |
| VALIDATION_FAILED | Rule failure |

---

# HTTP Status Codes

| Status | Meaning |
|---------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation Error |
| 404 | Not Found |
| 422 | Invalid Input |
| 500 | Internal Error |

---

# Pagination

Request

```
GET /invoices?page=1&limit=20
```

Response

```json
{
  "page":1,
  "limit":20,
  "total":250,
  "items":[]
}
```

---

# OpenAPI Tags

- Health
- Dashboard
- Invoices
- Vendors
- Purchase Orders
- Analytics

---

# Acceptance Criteria

- RESTful endpoints
- Consistent JSON contract
- Typed request/response models
- Pagination support
- Search and filtering
- OpenAPI compatible

---

# Antigravity Build Prompt

Generate FastAPI routers from this specification.

Create:

- invoices.py
- dashboard.py
- vendors.py
- purchase_orders.py
- history.py
- health.py

Requirements

- Use APIRouter
- Pydantic v2 models
- Dependency injection
- Repository pattern
- Automatic OpenAPI documentation
- Consistent error responses
