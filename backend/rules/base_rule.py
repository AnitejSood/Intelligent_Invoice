"""Base interface for all deterministic business rules."""

from abc import ABC, abstractmethod
from typing import Any
from backend.models.rule_result import RuleResult
from backend.llm.gemini_client import ExtractedInvoiceData

class BaseRule(ABC):
    """Abstract base class for all business rules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the rule."""
        pass
        
    @abstractmethod
    def evaluate(self, extracted_data: ExtractedInvoiceData, context: dict[str, Any]) -> RuleResult:
        """
        Evaluate the rule against the extracted data.
        Returns a RuleResult indicating PASS, FAIL, or WARNING.
        """
        pass
