"""Validation service for orchestrating business rules."""

from typing import Any
from backend.core.logging_config import get_logger
from backend.llm.gemini_client import ExtractedInvoiceData
from backend.models.rule_result import RuleResult
from backend.rules.impl import ACTIVE_RULES

logger = get_logger("rules.validation")

class ValidationService:
    """Runs all active business rules against extracted data."""
    
    @classmethod
    def run_all_rules(cls, data: ExtractedInvoiceData, context: dict[str, Any]) -> list[RuleResult]:
        """
        Execute all rules and return their results.
        Context dictionary provides external data (like DB lookup results).
        """
        logger.info(f"Running {len(ACTIVE_RULES)} business rules for invoice: {data.invoice_number}")
        results = []
        
        for rule in ACTIVE_RULES:
            try:
                result = rule.evaluate(data, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Rule {rule.name} failed during evaluation: {e}")
                results.append(RuleResult(
                    rule_name=rule.name,
                    result="FAIL",
                    expected="Successful evaluation",
                    actual="Exception",
                    message=f"Rule evaluation failed: {e}"
                ))
                
        # Count failures
        failures = sum(1 for r in results if r.result == "FAIL")
        logger.info(f"Rule execution complete. {failures} failures detected.")
        
        return results
