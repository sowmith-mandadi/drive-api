"""Test script for validating Google Slides extractor."""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.extractors.slides_extractor import SlidesExtractor
from app.api.drive_routes import get_drive_service

def test_slides_extractor():
    """Test the Google Slides extractor."""
    logger.info("Testing Google Slides extractor...")
    
    try:
        # First check Drive API access
        drive_service = get_drive_service()
        if not drive_service:
            logger.error("❌ Failed to initialize Drive service!")
            return False
            
        # Test with the provided Google Slides file ID
        sample_file_id = "1Vjg5HK1uI0rzMjwLh2Uwv4uqomDABECU99DKTXC6kIw"
        
        # Check if we can access the file through Drive API
        try:
            file = drive_service.files().get(
                fileId=sample_file_id,
                fields='id,name,mimeType'
            ).execute()
            logger.info(f"✅ Successfully accessed file through Drive API: {file.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"❌ Failed to access file through Drive API: {e}")
            return False
        
        # Initialize the extractor
        extractor = SlidesExtractor()
        
        # Extract text from the slides
        chunks = extractor.extract_text(sample_file_id)
        
        if chunks:
            logger.info(f"✅ Successfully extracted {len(chunks)} chunks from Google Slides!")
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"\nChunk {i}:")
                logger.info(f"Slide: {chunk.get('slide', 'N/A')}")
                logger.info(f"Slide ID: {chunk.get('slide_id', 'N/A')}")
                logger.info(f"Presentation ID: {chunk.get('presentation_id', 'N/A')}")
                # Construct the slide URL
                slide_url = f"https://docs.google.com/presentation/d/{chunk.get('presentation_id', '')}/edit#slide=id.{chunk.get('slide_id', '')}"
                logger.info(f"Slide URL: {slide_url}")
                logger.info(f"Text preview: {chunk.get('text', '')[:200]}...")
            return True
        else:
            logger.error("❌ No chunks were extracted from the slides")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing slides extractor: {e}")
        return False

if __name__ == "__main__":
    test_slides_extractor() 