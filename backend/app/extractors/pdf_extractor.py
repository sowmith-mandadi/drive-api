"""PDF content extractor module."""

import os
import logging
from typing import List, Dict, Any
from pypdf import PdfReader

# Initialize logger
logger = logging.getLogger(__name__)

class PdfExtractor:
    """Extracts content from PDF files."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        logger.info("Initializing PDF Extractor")
    
    def extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List[Dict]: List of text chunks with page information
        """
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return []
            
            # Create PDF reader object
            pdf = PdfReader(file_path)
            
            # Extract text from each page
            chunks = []
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                
                if page_text:
                    # Clean and format text
                    page_text = page_text.strip()
                    
                    # Skip empty pages
                    if not page_text:
                        continue
                    
                    # Add to chunks
                    chunks.append({
                        "text": page_text,
                        "page": i + 1
                    })
            
            logger.info(f"Extracted {len(chunks)} text chunks from PDF")
            return chunks
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return [] 