"""Structured logging configuration for FinanceFlow AI."""

import logging
import sys
from datetime import datetime


class FinanceFlowFormatter(logging.Formatter):
    """Custom log formatter with timestamp, level, and module context."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return (
            f"{color}[{timestamp}] "
            f"[{record.levelname:<8}] "
            f"[{record.name}] "
            f"{record.getMessage()}{self.RESET}"
        )


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    root_logger = logging.getLogger("financeflow")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(FinanceFlowFormatter())
        root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance scoped to financeflow."""
    return logging.getLogger(f"financeflow.{name}")
