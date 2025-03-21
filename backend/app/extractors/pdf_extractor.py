"""PDF content extractor module."""

import os
import logging
from typing import List, Dict, Any
from pypdf import PdfReader
# Remove PyPDF2 import as we'll use pypdf instead
# import PyPDF2

# Initialize logger
logger = logging.getLogger(__name__)

class PdfExtractor:
    """Extracts content from PDF files."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        logger.info("Initializing PDF Extractor")
    
    def extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text chunks with page numbers
        """
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            # Check if file exists and is not empty
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                logger.error(f"PDF file does not exist or is empty: {file_path}")
                return []
            
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object using pypdf instead of PyPDF2
                pdf = PdfReader(file)
                
                # Get the number of pages
                num_pages = len(pdf.pages)
                
                if num_pages == 0:
                    logger.warning(f"PDF has no pages: {file_path}")
                    return []
                
                logger.info(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                chunks = []
                for i in range(num_pages):
                    try:
                        # Get the page
                        page = pdf.pages[i]
                        
                        # Extract text
                        text = page.extract_text()
                        
                        if text and text.strip():
                            # Add chunk
                            chunks.append({
                                "text": text,
                                "page": i + 1
                            })
                    except Exception as e:
                        logger.error(f"Error extracting text from page {i+1}: {e}")
                        continue
                
                return chunks
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return [] 