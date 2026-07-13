# FinanceFlow AI

> AI-powered Accounts Payable Copilot — automates invoice processing with OCR, Gemini extraction, and deterministic business rules.

## Architecture

```
PDF Upload → Document Detection → OCR/Text Extraction → Gemini JSON Extraction → Python Rule Engine → Decision → Explanation
```

**Key Principle**: AI assists, never decides. Gemini extracts data and generates explanations. Python business rules make all financial decisions.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | Gemini 2.5 Flash |
| OCR | PaddleOCR, PyMuPDF, pdfplumber |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and add your Gemini API key.

## Project Structure

```
Invoice_Processing/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # React + Vite + TypeScript
├── Documentation/    # Design documents
├── sample_data/      # Test invoices
└── scripts/          # Utility scripts
```

## License

MIT
