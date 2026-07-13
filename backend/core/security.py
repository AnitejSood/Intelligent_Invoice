"""Security utilities — placeholder for future auth."""

# MVP: No authentication required.
# Future: JWT-based auth will be added here.

ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILENAME_LENGTH = 255


def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filenames."""
    import re
    # Keep only alphanumeric, hyphens, underscores, and dots
    sanitized = re.sub(r"[^\w\-.]", "_", filename)
    return sanitized[:MAX_FILENAME_LENGTH]


def validate_mime_type(content_type: str) -> bool:
    """Check if uploaded file MIME type is allowed."""
    return content_type in ALLOWED_MIME_TYPES
