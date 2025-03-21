"""PDF content extractor module."""

import os
import logging
from typing import List, Dict, Any

# Initialize logger
logger = logging.getLogger(__name__)

class PdfExtractor:
    """Extracts content from PDF files."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        logger.info("Initializing PDF Extractor")
        self.pdf_lib = None
        self.init_pdf_lib()
    
    def init_pdf_lib(self):
        """Initialize PDF library, trying different available libraries."""
        # Try to import PyPDF2
        try:
            import PyPDF2
            self.pdf_lib = "PyPDF2"
            logger.info("Using PyPDF2 library for PDF extraction")
            return
        except ImportError as e:
            logger.warning(f"PyPDF2 not available: {e}")
            logger.warning("Trying alternative libraries...")
        except Exception as e:
            logger.warning(f"Error importing PyPDF2: {e}")
            logger.warning("Trying alternative libraries...")
        
        # Try to import pypdf
        try:
            from pypdf import PdfReader
            self.pdf_lib = "pypdf"
            logger.info("Using pypdf library for PDF extraction")
            return
        except ImportError as e:
            logger.warning(f"pypdf not available: {e}")
        except Exception as e:
            logger.warning(f"Error importing pypdf: {e}")
        
        # Log more details about the environment
        import sys
        logger.error(f"No PDF extraction library available. Python version: {sys.version}")
        logger.error(f"Python path: {sys.executable}")
        logger.error(f"Path: {sys.path}")
        
        # Try to install pypdf at runtime if in development environment
        try:
            import subprocess
            logger.warning("Attempting to install PyPDF2 at runtime...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2==3.0.1"])
            import PyPDF2
            self.pdf_lib = "PyPDF2"
            logger.info("Successfully installed and imported PyPDF2")
            return
        except Exception as e:
            logger.error(f"Failed to install PyPDF2 at runtime: {e}")
        
        logger.error("No PDF extraction library available after all attempts")
    
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
            if not os.path.exists(file_path):
                logger.error(f"PDF file does not exist: {file_path}")
                return []
                
            if os.path.getsize(file_path) == 0:
                logger.error(f"PDF file is empty: {file_path}")
                return []
            
            # If no PDF library is available, return empty result
            if self.pdf_lib is None:
                logger.error("No PDF library available for text extraction")
                return []
            
            # Extract text based on available library
            if self.pdf_lib == "PyPDF2":
                return self._extract_with_pypdf2(file_path)
            elif self.pdf_lib == "pypdf":
                return self._extract_with_pypdf(file_path)
            else:
                logger.error(f"Unknown PDF library: {self.pdf_lib}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return []
    
    def _extract_with_pypdf2(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text using PyPDF2 library."""
        try:
            import PyPDF2
            
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
                pdf = PyPDF2.PdfReader(file)
                
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
            logger.error(f"Error with PyPDF2 extraction: {e}")
            return []
    
    def _extract_with_pypdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text using pypdf library."""
        try:
            from pypdf import PdfReader
            
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
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
            logger.error(f"Error with pypdf extraction: {e}")
            return [] 