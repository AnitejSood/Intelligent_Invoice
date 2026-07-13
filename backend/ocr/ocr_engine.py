"""PaddleOCR engine for scanned documents."""

import os
import fitz  # PyMuPDF
import numpy as np
from paddleocr import PaddleOCR
from backend.core.logging_config import get_logger

logger = get_logger("ocr.paddle_engine")

# Initialize PaddleOCR globally so the model is only loaded once
# use_angle_cls=True helps with rotated text
logger.info("Initializing PaddleOCR...")
# Suppress paddleocr's verbose debug logging
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

class OCREngine:
    """Uses PaddleOCR to extract text from images or scanned PDFs."""
    
    @classmethod
    def extract_text_from_pdf(cls, file_path: str) -> tuple[str, float]:
        """
        Extract text from a scanned PDF by rendering pages to images and running OCR.
        Returns a tuple of (extracted_text, average_confidence).
        """
        logger.info(f"Running PaddleOCR on scanned PDF: {file_path}")
        
        extracted_lines = []
        confidences = []
        
        try:
            doc = fitz.open(file_path)
            # Use a reasonable DPI for OCR (e.g., 200 or 300)
            zoom = 2.0  # roughly 144 DPI
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert PyMuPDF pixmap to numpy array for PaddleOCR
                img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                
                # If image is RGB, it's fine. If grayscale, convert to RGB.
                if pix.n == 1:
                    img_data = np.stack((img_data.squeeze(),)*3, axis=-1)
                
                # Run OCR
                # result is a list of lines, each line is [box, (text, confidence)]
                result = ocr_model.ocr(img_data, cls=True)
                
                if not result or not result[0]:
                    continue
                    
                # Process results
                page_lines = result[0]
                for line in page_lines:
                    text = line[1][0]
                    conf = line[1][1]
                    extracted_lines.append(text)
                    confidences.append(conf)
            
            doc.close()
            
            full_text = "\n".join(extracted_lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.debug(f"OCR completed. Avg confidence: {avg_confidence:.2f}")
            return full_text, avg_confidence
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed for {file_path}: {e}")
            raise
