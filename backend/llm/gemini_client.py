"""Gemini client for data extraction and explanation generation."""

import json
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from typing import Optional

from backend.core.config import settings
from backend.core.logging_config import get_logger

logger = get_logger("llm.gemini_client")

# Initialize client helper
def get_gemini_client() -> genai.Client:
    """Helper to initialize genai Client with settings API key."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


class ExtractedLineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float

class ExtractedInvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_gst: Optional[str] = None
    po_number: Optional[str] = None          # primary PO reference
    po_numbers: list[str] = []               # all PO references (for split-PO)
    invoice_date: Optional[str] = None       # YYYY-MM-DD
    subtotal: float = 0.0
    tax: float = 0.0
    shipping: float = 0.0
    total: float = 0.0
    currency: str = "INR"
    line_items: list[ExtractedLineItem] = []


class GeminiClient:
    """Client for interacting with Google Gemini API using modern google-genai SDK."""
    
    SYSTEM_PROMPT = """You are an enterprise invoice information extraction engine.
Your job is to extract information from invoices.
Return ONLY valid JSON matching the schema.
Never use markdown.
Never invent values.
If a value is missing, return null.
Do not perform financial validation.
Do not approve or reject invoices."""

    EXTRACTION_PROMPT = """Extract the following fields from this invoice:
- Vendor Name
- Invoice Number
- Invoice Date (format: YYYY-MM-DD)
- Purchase Order Number (single primary PO)
- All Purchase Order Numbers (list every PO reference found, even if only one)
- GST Number
- Currency
- Subtotal
- Tax
- Shipping
- Grand Total
- Line Items (description, quantity, unit_price, amount for each)

Important rules:
- If multiple PO numbers are referenced, list ALL of them in po_numbers
- Also set po_number to the first/primary PO
- Extract every line item you can find, even if formatting is messy
- Dates must be in YYYY-MM-DD format
- If currency symbol is ₹ or Rs, set currency to "INR"
"""

    EXPLANATION_SYSTEM_PROMPT = """You are assisting an Accounts Payable analyst.
The business rules have already produced a final decision.
Do not change the decision.
Explain it clearly for a finance user.
Be specific about which rules passed/failed and why.
Reference actual values where relevant."""

    EXPLANATION_PROMPT = """Decision: {decision}

Document Type: {doc_type}
Extraction Confidence: {confidence:.0%}
Vendor Match: {vendor_match}

Rule Results:
{rule_results}

Write a clear, detailed explanation in under 200 words suitable for an AP analyst.
Structure: Start with the decision, then list key findings, then any concerns."""

    @classmethod
    def extract_invoice_data(cls, text: str | None = None, images: list | None = None) -> ExtractedInvoiceData:
        """Extract invoice structured data using Schema Enforcement. Supports text or images (multimodal)."""
        try:
            client = get_gemini_client()
        except ValueError as e:
            logger.error(f"Initialization failed: {e}")
            return ExtractedInvoiceData()
            
        prompt = cls.EXTRACTION_PROMPT
        if text:
            prompt += f"\n\nInvoice Text:\n\"\"\"\n{text}\n\"\"\""
            
        # Combine text prompt and images into a single contents list
        contents = [prompt]
        if images:
            contents.extend(images)
            logger.info(f"Passing {len(images)} images to Gemini for Multimodal OCR.")
        
        try:
            # Generate content with guaranteed Pydantic schema structure
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=cls.SYSTEM_PROMPT,
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=ExtractedInvoiceData,
                )
            )
            
            raw_json = response.text
            data_dict = json.loads(raw_json)
            validated_data = ExtractedInvoiceData(**data_dict)
            
            # Ensure po_numbers includes po_number for consistency
            if validated_data.po_number and validated_data.po_number not in validated_data.po_numbers:
                validated_data.po_numbers.insert(0, validated_data.po_number)
            if not validated_data.po_number and validated_data.po_numbers:
                validated_data.po_number = validated_data.po_numbers[0]
                
            logger.info("Successfully extracted structured data with GenAI Schema Enforcement.")
            return validated_data
            
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"GenAI response validation failed: {e}")
        except Exception as e:
            logger.error(f"Gemini API error during extraction: {e}")
            
        logger.error("All Gemini extraction attempts failed.")
        return ExtractedInvoiceData()

    @classmethod
    def generate_explanation(cls, invoice_data: dict, rule_results: list[dict], decision: str,
                             doc_type: str = "UNKNOWN", confidence: float = 0.0,
                             vendor_match: str = "Unknown") -> str:
        """Generate a natural language explanation of the rule engine's decision."""
        try:
            client = get_gemini_client()
        except ValueError as e:
            logger.error(f"Initialization failed: {e}")
            return "AI explanation unavailable (API key not configured)."
            
        try:
            # Format rule results with full detail
            formatted_rules = "\n".join([
                f"- {r.get('rule_name', 'Rule')}: {r.get('result', 'FAIL')} | "
                f"Expected: {r.get('expected', 'N/A')} | "
                f"Actual: {r.get('actual', 'N/A')} | "
                f"{r.get('message', '')}"
                for r in rule_results
            ])
            
            prompt = cls.EXPLANATION_PROMPT.format(
                decision=decision,
                doc_type=doc_type,
                confidence=confidence,
                vendor_match=vendor_match,
                rule_results=formatted_rules
            )
            
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=cls.EXPLANATION_SYSTEM_PROMPT,
                    temperature=0.2,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return "Explanation generation failed."
