"""Settings service — persists business rules parameters dynamically."""

import os
import json
from backend.core.config import settings
from backend.core.logging_config import get_logger

logger = get_logger("services.settings")
SETTINGS_FILE = "settings.json"

class SettingsService:
    """Service to load and store business validation rules settings dynamically."""

    @classmethod
    def get_all(cls) -> dict:
        """Get all settings, falling back to config defaults."""
        defaults = {
            "PO_TOLERANCE_PERCENT": settings.PO_TOLERANCE_PERCENT,
            "MAX_INVOICE_AGE_DAYS": settings.MAX_INVOICE_AGE_DAYS,
            "REQUIRE_GST": settings.REQUIRE_GST,
            "REQUIRE_PO": settings.REQUIRE_PO,
            "DUPLICATE_DETECTION_DAYS": settings.DUPLICATE_DETECTION_DAYS,
            "MIN_CONFIDENCE_THRESHOLD": settings.MIN_CONFIDENCE_THRESHOLD,
            "REQUIRE_LINE_ITEMS_MATCH": settings.REQUIRE_LINE_ITEMS_MATCH,
            "EMAIL_INGESTION_ENABLED": settings.EMAIL_INGESTION_ENABLED,
            "EMAIL_SERVER": settings.EMAIL_SERVER,
            "EMAIL_ADDRESS": settings.EMAIL_ADDRESS,
            "EMAIL_PASSWORD": settings.EMAIL_PASSWORD,
            "ERP_SYNC_ENABLED": settings.ERP_SYNC_ENABLED,
            "ERP_WEBHOOK_URL": settings.ERP_WEBHOOK_URL,
        }
        
        if not os.path.exists(SETTINGS_FILE):
            # Save defaults on first run
            cls.save(defaults)
            return defaults
            
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
            # Ensure all keys exist
            for k, v in defaults.items():
                if k not in saved:
                    saved[k] = v
            return saved
        except Exception as e:
            logger.error(f"Failed to read settings: {e}")
            return defaults

    @classmethod
    def save(cls, new_settings: dict) -> bool:
        """Persist new settings to JSON file."""
        try:
            # Ensure types are validated/coerced
            payload = {
                "PO_TOLERANCE_PERCENT": float(new_settings.get("PO_TOLERANCE_PERCENT", settings.PO_TOLERANCE_PERCENT)),
                "MAX_INVOICE_AGE_DAYS": int(new_settings.get("MAX_INVOICE_AGE_DAYS", settings.MAX_INVOICE_AGE_DAYS)),
                "REQUIRE_GST": bool(new_settings.get("REQUIRE_GST", settings.REQUIRE_GST)),
                "REQUIRE_PO": bool(new_settings.get("REQUIRE_PO", settings.REQUIRE_PO)),
                "DUPLICATE_DETECTION_DAYS": int(new_settings.get("DUPLICATE_DETECTION_DAYS", settings.DUPLICATE_DETECTION_DAYS)),
                "MIN_CONFIDENCE_THRESHOLD": int(new_settings.get("MIN_CONFIDENCE_THRESHOLD", settings.MIN_CONFIDENCE_THRESHOLD)),
                "REQUIRE_LINE_ITEMS_MATCH": bool(new_settings.get("REQUIRE_LINE_ITEMS_MATCH", settings.REQUIRE_LINE_ITEMS_MATCH)),
                "EMAIL_INGESTION_ENABLED": bool(new_settings.get("EMAIL_INGESTION_ENABLED", settings.EMAIL_INGESTION_ENABLED)),
                "EMAIL_SERVER": str(new_settings.get("EMAIL_SERVER", settings.EMAIL_SERVER)),
                "EMAIL_ADDRESS": str(new_settings.get("EMAIL_ADDRESS", settings.EMAIL_ADDRESS)),
                "EMAIL_PASSWORD": str(new_settings.get("EMAIL_PASSWORD", settings.EMAIL_PASSWORD)),
                "ERP_SYNC_ENABLED": bool(new_settings.get("ERP_SYNC_ENABLED", settings.ERP_SYNC_ENABLED)),
                "ERP_WEBHOOK_URL": str(new_settings.get("ERP_WEBHOOK_URL", settings.ERP_WEBHOOK_URL)),
            }
            with open(SETTINGS_FILE, "w") as f:
                json.dump(payload, f, indent=4)
            logger.info("Successfully updated validation rule configurations.")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
