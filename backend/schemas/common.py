"""Common Pydantic schemas used across the application."""

from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    success: bool = False
    message: str
    code: str


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    items: list[Any] = []
    total: int = 0
    page: int = 1
    limit: int = 20
