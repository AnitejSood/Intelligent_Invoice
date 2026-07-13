"""Processing Log model — stores timeline of processing stages."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database.base import Base


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    stage = Column(String, nullable=False)  # Upload | Detection | OCR | Extraction | Validation | Decision | Save
    status = Column(String, nullable=False)  # STARTED | COMPLETED | FAILED
    duration_ms = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON string for extra info
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="processing_logs")

    def __repr__(self) -> str:
        return f"<ProcessingLog(stage='{self.stage}', status='{self.status}')>"
