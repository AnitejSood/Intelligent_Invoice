"""Document type detector (Digital vs Scanned)."""

import fitz  # PyMuPDF
from backend.core.logging_config import get_logger

logger = get_logger("ocr.document_detector")

class DocumentDetector:
    """Detects whether a PDF is digital (text-based) or scanned (image-based)."""
    
    TEXT_THRESHOLD = 50  # characters
    
    @classmethod
    def detect_type(cls, file_path: str) -> str:
        """
        Analyze the PDF to determine its type.
        Returns 'DIGITAL' or 'SCANNED'.
        """
        try:
            doc = fitz.open(file_path)
            total_text = ""
            
            # Check first few pages to determine type
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                total_text += page.get_text("text").strip()
                
                if len(total_text) > cls.TEXT_THRESHOLD:
                    doc.close()
                    logger.debug(f"Detected DIGITAL document: {file_path}")
                    return "DIGITAL"
                    
            doc.close()
            logger.debug(f"Detected SCANNED document: {file_path}")
            return "SCANNED"
            
        except Exception as e:
            logger.error(f"Failed to detect document type for {file_path}: {e}")
            # Fallback to scanned to force OCR if we can't read it normally
            return "SCANNED"
