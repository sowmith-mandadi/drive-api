"""
Test script for validating various services in the Conference Content Management API.
This script will test each service to ensure it's working correctly with the proper credentials.
"""

import os
import sys
import json
import logging
import requests
import base64
import tempfile
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from config
sys.path.insert(0, str(Path(__file__).parent))

# Try importing directly from the backend
try:
    from app.services.content_service import ContentService
    from app.services.rag_service import RAGService
    from app.services.embedding_service import EmbeddingService
    from app.repository.storage_repo import StorageRepository
    from app.repository.firestore_repo import FirestoreRepository
    from app.repository.vector_repo import VectorRepository
    direct_import = True
except ImportError:
    logger.warning("Could not import directly from app services. Will test via HTTP API.")
    direct_import = False

# Set API base URL - default to localhost:3001 if not set
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3001/api")

def test_health_api():
    """Test the health API endpoints."""
    logger.info("Testing health API endpoints...")
    
    # Basic health check
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        logger.info("✅ Health endpoint is working!")
        data = response.json()
        logger.info(f"API version: {data.get('version', 'unknown')}")
    else:
        logger.error(f"❌ Health endpoint failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False
    
    # System info check
    response = requests.get(f"{API_BASE_URL}/health/info")
    if response.status_code == 200:
        logger.info("✅ Health info endpoint is working!")
        data = response.json()
        logger.info(f"Python version: {data.get('python_version', 'unknown')}")
        logger.info(f"Platform: {data.get('platform', 'unknown')}")
    else:
        logger.error(f"❌ Health info endpoint failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False
    
    return True

def test_content_api():
    """Test the content API endpoints."""
    logger.info("Testing content API endpoints...")
    
    # Get recent content
    response = requests.get(f"{API_BASE_URL}/recent-content")
    if response.status_code == 200:
        logger.info("✅ Recent content endpoint is working!")
        data = response.json()
        content_count = len(data.get('content', []))
        logger.info(f"Found {content_count} recent content items")
    else:
        logger.error(f"❌ Recent content endpoint failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False
    
    # Get popular tags
    response = requests.get(f"{API_BASE_URL}/popular-tags")
    if response.status_code == 200:
        logger.info("✅ Popular tags endpoint is working!")
        
        # Parse the response - handle direct list or dict with 'tags' key
        data = response.json()
        logger.info(f"Popular tags data: {data}")  # Debug log
        
        if isinstance(data, list):
            # Direct list of tags
            tags = data
            tag_count = len(tags)
            logger.info(f"Found {tag_count} popular tags (direct list)")
        else:
            # Dictionary containing tags
            tags = data.get('tags', [])
            
            # Handle different dictionary response formats
            if isinstance(tags, list):
                tag_count = len(tags)
                logger.info(f"Found {tag_count} popular tags (dict.list)")
            elif isinstance(tags, dict):
                tag_count = len(tags.keys())
                logger.info(f"Found {tag_count} popular tags (dict.dict)")
            else:
                logger.info(f"Popular tags format is not as expected: {type(tags)}")
    else:
        logger.error(f"❌ Popular tags endpoint failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False
    
    return True

def test_upload_content_with_file():
    """Test uploading content with a file attachment."""
    logger.info("Testing content upload with file...")
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
        temp.write(b"This is test content for the conference management API.")
        temp_path = temp.name
    
    try:
        # Prepare upload data
        metadata = {
            "title": "Test Upload",
            "description": "This is a test upload from the test script",
            "presenter": "Test User",
            "email": "test@example.com",
            "tags": ["test", "api", "upload"],
            "track": "Testing Track",
            "presentationDate": datetime.now().isoformat()
        }
        
        # Create multipart form data
        files = {
            'file': ('test_file.txt', open(temp_path, 'rb'), 'text/plain'),
            'metadata': (None, json.dumps(metadata))
        }
        
        # Upload content
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            logger.info("✅ Content upload with file is working!")
            data = response.json()
            logger.info(f"Upload response: {data}")
            return True
        else:
            logger.error(f"❌ Content upload failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error during content upload test: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_rag_api():
    """Test the RAG API endpoints."""
    logger.info("Testing RAG API endpoints...")
    
    # Test RAG question answering
    question_data = {
        "question": "What is machine learning?",
        "contentIds": [],
        "filters": {"tracks": [], "tags": []}
    }
    
    response = requests.post(f"{API_BASE_URL}/rag/ask", json=question_data)
    if response.status_code == 200:
        logger.info("✅ RAG question answering is working!")
        data = response.json()
        answer = data.get('answer', '')
        logger.info(f"Answer preview: {answer[:100]}...")
    else:
        logger.error(f"❌ RAG question answering failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False
    
    # Test RAG summarization
    if response.status_code == 200:
        # Get first content item for testing summarization
        content_response = requests.get(f"{API_BASE_URL}/recent-content")
        if content_response.status_code == 200:
            content_data = content_response.json()
            if content_data.get('content'):
                content_id = content_data['content'][0].get('id')
                
                if content_id:
                    summarize_data = {
                        "contentId": content_id
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/rag/summarize", json=summarize_data)
                    if response.status_code == 200:
                        logger.info("✅ RAG summarization is working!")
                        data = response.json()
                        summary = data.get('summary', '')
                        logger.info(f"Summary preview: {summary[:100]}...")
                    else:
                        logger.error(f"❌ RAG summarization failed with status code {response.status_code}")
                        logger.error(f"Response: {response.text}")
            else:
                logger.warning("⚠️ No content items found for testing summarization")
        else:
            logger.error(f"❌ Failed to get content for summarization test")
    
    return True

def test_content_service_direct():
    """Test the ContentService directly."""
    if not direct_import:
        logger.warning("Skipping direct ContentService test due to import error")
        return True
    
    logger.info("Testing ContentService directly...")
    
    try:
        # Initialize service
        content_service = ContentService()
        
        # Test getting recent content
        recent_content = content_service.get_recent_content(limit=5)
        logger.info(f"✅ ContentService initialized successfully! Retrieved {len(recent_content)} content items.")
        
        # Test getting popular tags
        popular_tags = content_service.get_popular_tags(limit=10)
        logger.info(f"✅ Retrieved {len(popular_tags)} popular tags.")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing ContentService: {e}")
        return False

def test_rag_service_direct():
    """Test the RAGService directly."""
    if not direct_import:
        logger.warning("Skipping direct RAGService test due to import error")
        return True
    
    logger.info("Testing RAGService directly...")
    
    try:
        # Initialize service
        rag_service = RAGService()
        
        # Test answering a question
        answer = rag_service.ask_question("What is machine learning?", [])
        logger.info(f"✅ RAGService initialized successfully! Got answer preview: {answer[:100]}...")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing RAGService: {e}")
        return False

def test_embedding_service_direct():
    """Test the EmbeddingService directly."""
    if not direct_import:
        logger.warning("Skipping direct EmbeddingService test due to import error")
        return True
    
    logger.info("Testing EmbeddingService directly...")
    
    try:
        # Initialize service
        embedding_service = EmbeddingService()
        
        # Test generating embeddings
        text = "This is a test document for embedding generation."
        embedding = embedding_service.get_embeddings(text)
        
        if embedding and len(embedding) > 0:
            logger.info(f"✅ EmbeddingService initialized successfully! Generated embedding of dimension {len(embedding)}.")
            return True
        else:
            logger.error("❌ Failed to generate embeddings.")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing EmbeddingService: {e}")
        return False

def test_storage_repository_direct():
    """Test the StorageRepository directly."""
    if not direct_import:
        logger.warning("Skipping direct StorageRepository test due to import error")
        return True
    
    logger.info("Testing StorageRepository directly...")
    
    try:
        # Initialize repository
        storage_repo = StorageRepository()
        
        # Test listing files
        files = storage_repo.list_files(prefix="test", limit=5)
        logger.info(f"✅ StorageRepository initialized successfully! Listed {len(files)} files.")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing StorageRepository: {e}")
        return False

def test_firestore_repository_direct():
    """Test the FirestoreRepository directly."""
    if not direct_import:
        logger.warning("Skipping direct FirestoreRepository test due to import error")
        return True
    
    logger.info("Testing FirestoreRepository directly...")
    
    try:
        # Initialize repository
        firestore_repo = FirestoreRepository()
        
        # Test getting collection
        collection_name = "content"
        docs = firestore_repo.get_collection(collection_name, limit=5)
        logger.info(f"✅ FirestoreRepository initialized successfully! Retrieved {len(docs)} documents from {collection_name}.")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing FirestoreRepository: {e}")
        return False

def run_all_tests():
    """Run all service tests."""
    logger.info("Starting services integration tests")
    
    # HTTP API tests
    health_ok = test_health_api()
    content_ok = test_content_api()
    rag_ok = test_rag_api()
    upload_ok = test_upload_content_with_file()
    
    # Direct service tests (if possible)
    if direct_import:
        logger.info("\nRunning direct service tests...")
        content_service_ok = test_content_service_direct()
        rag_service_ok = test_rag_service_direct()
        embedding_service_ok = test_embedding_service_direct()
        storage_repo_ok = test_storage_repository_direct()
        firestore_repo_ok = test_firestore_repository_direct()
    else:
        content_service_ok = True
        rag_service_ok = True
        embedding_service_ok = True
        storage_repo_ok = True
        firestore_repo_ok = True
        logger.warning("Direct service tests skipped due to import errors")
    
    # Summary
    logger.info("\n=== Test Results ===")
    logger.info(f"Health API: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    logger.info(f"Content API: {'✅ PASSED' if content_ok else '❌ FAILED'}")
    logger.info(f"RAG API: {'✅ PASSED' if rag_ok else '❌ FAILED'}")
    logger.info(f"Content Upload: {'✅ PASSED' if upload_ok else '❌ FAILED'}")
    
    if direct_import:
        logger.info(f"ContentService: {'✅ PASSED' if content_service_ok else '❌ FAILED'}")
        logger.info(f"RAGService: {'✅ PASSED' if rag_service_ok else '❌ FAILED'}")
        logger.info(f"EmbeddingService: {'✅ PASSED' if embedding_service_ok else '❌ FAILED'}")
        logger.info(f"StorageRepository: {'✅ PASSED' if storage_repo_ok else '❌ FAILED'}")
        logger.info(f"FirestoreRepository: {'✅ PASSED' if firestore_repo_ok else '❌ FAILED'}")
    
    # Overall result
    http_tests = [health_ok, content_ok, rag_ok, upload_ok]
    service_tests = []
    if direct_import:
        service_tests = [content_service_ok, rag_service_ok, embedding_service_ok, storage_repo_ok, firestore_repo_ok]
    
    if all(http_tests) and all(service_tests):
        logger.info("\n✅ All tests passed! Services are working correctly.")
        return True
    else:
        logger.info("\n❌ Some tests failed. Check the log for details.")
        return False

if __name__ == "__main__":
    run_all_tests() 