"""PDF text extractor for digital documents."""

import pdfplumber
from backend.core.logging_config import get_logger

logger = get_logger("ocr.pdf_extractor")

class PDFExtractor:
    """Extracts layout-preserved text from digital PDFs using pdfplumber."""
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        Extract text from a digital PDF, preserving layout where possible.
        """
        logger.info(f"Extracting text from digital PDF: {file_path}")
        text_content = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # extract_text(layout=True) attempts to keep spatial layout
                    text = page.extract_text(layout=True)
                    if text:
                        text_content.append(text)
                        
            full_text = "\n\n".join(text_content)
            logger.debug(f"Successfully extracted {len(full_text)} characters.")
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to extract text using pdfplumber for {file_path}: {e}")
            raise
