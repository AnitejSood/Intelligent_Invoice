"""FinanceFlow AI — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time

from backend.core.config import settings
from backend.core.logging_config import setup_logging, get_logger
from backend.database.base import Base
from backend.database.session import engine

# Import all models so they're registered with Base.metadata
from backend.models import (  # noqa: F401
    Vendor, PurchaseOrder, Invoice,
    InvoiceLineItem, RuleResult, ProcessingLog,
)

# Import routers
from backend.api.health import router as health_router
from backend.api.invoices import router as invoices_router
from backend.api.dashboard import router as dashboard_router
from backend.api.history import router as history_router
from backend.api.vendors import router as vendors_router
from backend.api.purchase_orders import router as purchase_orders_router
from backend.api.settings import router as settings_router

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create tables (development only — use Alembic in production)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Auto-seed database (Crucial for ephemeral Free tier hosting)
    try:
        from backend.database import seed
        seed.main()
        logger.info("Database auto-seeding completed.")
    except Exception as e:
        logger.error(f"Auto-seeding failed: {e}")

    # Ensure upload directory exists
    settings.upload_path
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")

    # Start Background Tasks
    import asyncio
    from backend.services.imap_service import ImapService
    
    async def email_polling_task():
        """Background task to periodically poll the IMAP inbox."""
        logger.info("Email ingestion background task started.")
        while True:
            try:
                # Polling interval is every 60 seconds
                await asyncio.sleep(60)
                # Run the blocking IMAP logic in a thread pool to prevent blocking the async event loop
                invoices_processed = await asyncio.to_thread(ImapService.poll_inbox)
                if invoices_processed > 0:
                    logger.info(f"Email ingestion processed {invoices_processed} new invoices.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in email polling task: {e}")
                
    task = asyncio.create_task(email_polling_task())

    yield

    # Shutdown
    task.cancel()
    logger.info("Shutting down FinanceFlow AI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Accounts Payable Copilot — invoice processing with OCR, Gemini extraction, and deterministic business rules.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.1f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal error occurred",
            "code": "INTERNAL_ERROR",
        },
    )


# Mount routers under /api/v1
API_PREFIX = "/api/v1"

app.include_router(health_router, prefix=API_PREFIX)
app.include_router(invoices_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(history_router, prefix=API_PREFIX)
app.include_router(vendors_router, prefix=API_PREFIX)
app.include_router(purchase_orders_router, prefix=API_PREFIX)
app.include_router(settings_router, prefix=API_PREFIX)

# Mount static uploads directory for PDF preview
import os
upload_dir = settings.UPLOAD_DIR
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.get("/")
async def root():
    """Root endpoint — redirect info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
