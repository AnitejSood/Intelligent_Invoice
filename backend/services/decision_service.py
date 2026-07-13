"""Decision service to determine final invoice status."""

from backend.models.rule_result import RuleResult
from backend.core.logging_config import get_logger

logger = get_logger("rules.decision")

class DecisionService:
    """Combines rule outcomes into a final decision."""
    
    @staticmethod
    def determine_status(rule_results: list[RuleResult], extraction_confidence: float) -> str:
        """
        Determine final status: APPROVED, REJECTED, or PENDING_MANUAL_REVIEW
        """
        # 1. Reject if Duplicate Check fails
        duplicate_failures = [r for r in rule_results if r.rule_name == "Duplicate Check" and r.result == "FAIL"]
        if duplicate_failures:
            logger.info("Decision: REJECTED due to Duplicate Check failure.")
            return "REJECTED"
            
        # 2. Any other rule failures = PENDING_MANUAL_REVIEW
        failures = [r for r in rule_results if r.result == "FAIL"]
        if failures:
            logger.info(f"Decision: PENDING_MANUAL_REVIEW due to {len(failures)} rule failures.")
            return "PENDING_MANUAL_REVIEW"
            
        # 3. Confidence below threshold = PENDING_MANUAL_REVIEW
        if extraction_confidence < 0.70:
            logger.info(f"Decision: PENDING_MANUAL_REVIEW due to low confidence ({extraction_confidence:.2f}).")
            return "PENDING_MANUAL_REVIEW"
            
        # 4. Otherwise, APPROVED
        logger.info("Decision: APPROVED. All rules passed and confidence is high.")
        return "APPROVED"
