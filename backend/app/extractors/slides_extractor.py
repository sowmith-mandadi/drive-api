"""Google Slides content extractor module."""

import logging
from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Initialize logger
logger = logging.getLogger(__name__)

class SlidesExtractor:
    """Extracts content from Google Slides files."""
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initialize the Google Slides extractor.
        
        Args:
            credentials_path: Path to the service account credentials file
        """
        logger.info("Initializing Google Slides Extractor")
        self.credentials_path = credentials_path
        self._slides_service = None
    
    def _get_slides_service(self):
        """Get an authorized Google Slides API service."""
        if not self._slides_service:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/presentations.readonly']
                )
                self._slides_service = build('slides', 'v1', credentials=credentials)
            except Exception as e:
                logger.error(f"Error initializing Slides service: {e}")
                return None
        return self._slides_service
    
    def extract_text(self, file_id: str) -> List[Dict[str, Any]]:
        """Extract text content from a Google Slides file.
        
        Args:
            file_id: Google Drive file ID of the presentation
            
        Returns:
            List[Dict]: List of text chunks with slide information
        """
        try:
            logger.info(f"Processing Google Slides file: {file_id}")
            
            slides_service = self._get_slides_service()
            if not slides_service:
                logger.error("Could not initialize Slides service")
                return []
            
            # Get presentation details
            presentation = slides_service.presentations().get(
                presentationId=file_id,
                fields='slides'
            ).execute()
            
            if not presentation or 'slides' not in presentation:
                logger.error("No slides found in presentation")
                return []
            
            # Extract text from each slide
            chunks = []
            
            for i, slide in enumerate(presentation['slides']):
                slide_text = []
                slide_id = slide.get('objectId', '')
                
                # Extract text from all shapes in the slide
                for element in slide.get('pageElements', []):
                    if 'shape' in element:
                        shape = element['shape']
                        if 'text' in shape:
                            text_content = shape['text']
                            for text_element in text_content.get('textElements', []):
                                if 'textRun' in text_element:
                                    text = text_element['textRun'].get('content', '').strip()
                                    if text:
                                        slide_text.append(text)
                
                # Combine all text from the slide
                if slide_text:
                    combined_text = "\n".join(slide_text)
                    
                    # Skip empty slides
                    if not combined_text.strip():
                        continue
                    
                    # Add to chunks with slide ID
                    chunks.append({
                        "text": combined_text,
                        "slide": i + 1,
                        "slide_id": slide_id,
                        "presentation_id": file_id
                    })
            
            logger.info(f"Extracted {len(chunks)} text chunks from Google Slides")
            return chunks
        
        except Exception as e:
            logger.error(f"Error extracting text from Google Slides: {e}")
            return [] 