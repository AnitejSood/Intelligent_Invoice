"""Application configuration loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "FinanceFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./financeflow.db"

    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # OCR
    OCR_CONFIDENCE_THRESHOLD: int = 70

    # Business Rules
    PO_TOLERANCE_PERCENT: float = 5.0
    MAX_INVOICE_AGE_DAYS: int = 365
    REQUIRE_GST: bool = True
    REQUIRE_PO: bool = True
    DUPLICATE_DETECTION_DAYS: int = 90
    MIN_CONFIDENCE_THRESHOLD: int = 85
    REQUIRE_LINE_ITEMS_MATCH: bool = True

    # Email Integration
    EMAIL_INGESTION_ENABLED: bool = False
    EMAIL_SERVER: str = "imap.gmail.com"
    EMAIL_ADDRESS: str = ""
    EMAIL_PASSWORD: str = ""

    # Webhooks & Integrations
    ERP_SYNC_ENABLED: bool = False
    ERP_WEBHOOK_URL: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def upload_path(self) -> Path:
        """Return resolved upload directory path."""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
