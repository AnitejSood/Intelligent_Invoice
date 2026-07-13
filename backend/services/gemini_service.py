"""Gemini service — AI extraction and explanation."""

from backend.llm.gemini_client import GeminiClient, ExtractedInvoiceData
from backend.core.logging_config import get_logger

logger = get_logger("services.gemini")

class GeminiService:
    """Service layer for AI extraction and explanation."""
    
    @classmethod
    def extract_data(cls, text: str | None = None, images: list | None = None) -> ExtractedInvoiceData:
        """
        Extract structured invoice data using Gemini.
        Returns empty/default data if extraction fails.
        """
        logger.info(f"Starting Gemini data extraction. Text length: {len(text) if text else 0}, Images: {len(images) if images else 0}")
        try:
            extracted_data = GeminiClient.extract_invoice_data(text=text, images=images)
            return extracted_data
        except Exception as e:
            logger.error(f"Error in GeminiService extraction: {e}")
            return ExtractedInvoiceData()
            
    @classmethod
    def explain_decision(cls, extracted_data: ExtractedInvoiceData, rule_results: list, decision: str,
                         doc_type: str = "UNKNOWN", confidence: float = 0.0,
                         vendor_match: str = "Unknown") -> str:
        """
        Generate an explanation for the final processing decision.
        """
        logger.info("Generating explanation for decision.")
        try:
            explanation = GeminiClient.generate_explanation(
                invoice_data=extracted_data.model_dump(),
                rule_results=[
                    {
                        "rule_name": r.rule_name,
                        "result": r.result,
                        "expected": r.expected,
                        "actual": r.actual,
                        "message": r.message
                    } for r in rule_results
                ],
                decision=decision,
                doc_type=doc_type,
                confidence=confidence,
                vendor_match=vendor_match,
            )
            return explanation
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Explanation generation failed due to service error."
