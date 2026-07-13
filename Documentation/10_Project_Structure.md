# 10_Project_Structure.md

# FinanceFlow AI – Project Structure

Version: 1.0

---

# Purpose

This document defines the repository layout, coding standards, naming conventions, and development organization for FinanceFlow AI.

The structure is designed for:

- Maintainability
- Scalability
- Clean Architecture
- Easy onboarding
- AI-assisted development (Antigravity)

---

# Repository Structure

```text
FinanceFlow-AI/
├── backend/
├── frontend/
├── docs/
├── sample_data/
├── scripts/
├── assets/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

# Backend Structure

```text
backend/
├── api/
│   ├── dashboard.py
│   ├── health.py
│   ├── history.py
│   ├── invoices.py
│   ├── purchase_orders.py
│   └── vendors.py
├── core/
│   ├── config.py
│   ├── logging.py
│   └── security.py
├── database/
│   ├── base.py
│   ├── seed.py
│   └── session.py
├── models/
├── repositories/
├── schemas/
├── services/
├── rules/
├── ocr/
├── llm/
├── utils/
├── uploads/
├── tests/
└── main.py
```

---

# Frontend Structure

```text
frontend/
├── src/
│   ├── app/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── layouts/
│   ├── lib/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── styles/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── public/
└── package.json
```

---

# Components

Organize by feature.

Example

```text
components/
├── common/
├── dashboard/
├── history/
├── invoice/
├── timeline/
└── upload/
```

No business logic inside UI components.

---

# Naming Conventions

Python

- snake_case for files/functions
- PascalCase for classes

React

- PascalCase for components
- camelCase for hooks/utilities

Routes

- lowercase
- kebab-case URLs

---

# Environment Variables

Backend

```text
GEMINI_API_KEY=
DATABASE_URL=
UPLOAD_DIR=
MAX_UPLOAD_SIZE_MB=20
PO_TOLERANCE_PERCENT=5
OCR_CONFIDENCE_THRESHOLD=70
```

Frontend

```text
VITE_API_URL=
```

---

# Sample Data

```text
sample_data/
├── invoices/
├── purchase_orders.csv
├── vendors.csv
└── historical_invoices.csv
```

---

# Scripts

```text
scripts/
├── seed_db.py
├── generate_fake_data.py
├── reset_db.py
└── export_demo_data.py
```

---

# Documentation

```text
docs/
01_Product_Requirements_Document.md
02_System_Architecture.md
...
22_Design_System.md
```

---

# Git Workflow

Main Branch

- main

Feature Branches

- feature/backend
- feature/frontend
- feature/ocr
- feature/ui

Commit Style

- feat:
- fix:
- docs:
- refactor:
- chore:

---

# Coding Standards

- Type hints in Python
- Async FastAPI endpoints where appropriate
- Reusable services
- No duplicated logic
- Keep components under ~300 lines where possible
- Prefer composition over inheritance

---

# Build Order

1. Initialize backend
2. Initialize frontend
3. Database
4. Upload API
5. OCR
6. Gemini
7. Rule Engine
8. Dashboard
9. History
10. Polish UI

---

# Acceptance Criteria

- Consistent folder layout
- Clear separation of concerns
- Environment-driven configuration
- Feature-oriented frontend
- Modular backend
- Ready for CI/CD

---

# Antigravity Build Prompt

Scaffold the entire repository exactly as defined.

Create all folders, placeholder files, configuration files, and base modules.

Do not implement business logic yet.

Generate:

- FastAPI project
- React Vite project
- Shared folder structure
- Environment templates
- Seed scripts
- README placeholders

The scaffold should compile successfully before feature implementation begins.
