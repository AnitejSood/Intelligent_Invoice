"""OCR service orchestrator."""

import re
from backend.core.logging_config import get_logger
from backend.ocr.document_detector import DocumentDetector
from backend.ocr.pdf_extractor import PDFExtractor
from backend.ocr.ocr_engine import OCREngine

logger = get_logger("ocr.service")

class OCRService:
    """Orchestrates document detection and text extraction."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Standardize spacing and line breaks."""
        if not text:
            return ""
        # Remove multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Remove more than 2 consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @classmethod
    def process_document(cls, file_path: str) -> tuple[str, str, float]:
        """
        Main entry point for document text extraction.
        Returns:
            (document_type, extracted_text, confidence_score)
        """
        logger.info(f"Starting OCR processing for: {file_path}")
        
        # 1. Detect type
        doc_type = DocumentDetector.detect_type(file_path)
        logger.info(f"Document type detected as: {doc_type}")
        
        # 2. Extract text based on type
        text = ""
        confidence = 0.0
        
        if doc_type == "DIGITAL":
            text = PDFExtractor.extract_text(file_path)
            confidence = 1.0  # Digital text has 100% confidence
            
            # Fallback if digital extraction fails or returns very little text
            if len(text.strip()) < 50:
                logger.warning("Digital extraction yielded little text. Falling back to OCR.")
                doc_type = "SCANNED"
                
        if doc_type == "SCANNED":
            text, confidence = OCREngine.extract_text_from_pdf(file_path)
            
        # 3. Normalize text
        normalized_text = cls.normalize_text(text)
        
        logger.info(f"OCR processing complete. Extracted {len(normalized_text)} chars with {confidence:.2f} confidence.")
        return doc_type, normalized_text, confidence
