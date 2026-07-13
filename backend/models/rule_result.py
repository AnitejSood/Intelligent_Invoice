"""Rule Result model — stores each rule evaluation for audit."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database.base import Base


class RuleResult(Base):
    __tablename__ = "rule_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    rule_name = Column(String, nullable=False)
    result = Column(String, nullable=False)  # PASS | FAIL | WARNING
    expected = Column(String)
    actual = Column(String)
    message = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="rule_results")

    def __repr__(self) -> str:
        return f"<RuleResult(rule='{self.rule_name}', result='{self.result}')>"
