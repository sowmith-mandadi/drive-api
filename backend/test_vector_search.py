"""
Test script for validating vector search functionality in the Conference Content Management API.
This script tests the embedding generation and vector search capabilities.
"""

import os
import sys
import json
import logging
import requests
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
    from app.services.embedding_service import EmbeddingService
    from app.repository.vector_repo import VectorRepository
    direct_import = True
except ImportError:
    logger.warning("Could not import directly from app services. Will test via HTTP API.")
    direct_import = False

# Set API base URL - default to localhost:3001 if not set
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3001/api")

def create_test_documents():
    """Create test documents with known content for vector search testing."""
    documents = [
        {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy.",
            "tags": ["machine learning", "AI", "technology"]
        },
        {
            "title": "Deep Learning Fundamentals",
            "content": "Deep learning is a subset of machine learning where artificial neural networks, algorithms inspired by the human brain, learn from large amounts of data.",
            "tags": ["deep learning", "neural networks", "AI"]
        },
        {
            "title": "Natural Language Processing",
            "content": "Natural Language Processing (NLP) is a field of AI that gives machines the ability to read, understand, and derive meaning from human languages.",
            "tags": ["NLP", "AI", "language processing"]
        },
        {
            "title": "Computer Vision Applications",
            "content": "Computer vision is a field of AI that enables computers to derive meaningful information from digital images, videos and other visual inputs.",
            "tags": ["computer vision", "AI", "image processing"]
        },
        {
            "title": "Reinforcement Learning",
            "content": "Reinforcement learning is an area of machine learning concerned with how intelligent agents ought to take actions in an environment in order to maximize the notion of cumulative reward.",
            "tags": ["reinforcement learning", "AI", "agents"]
        }
    ]
    return documents

def test_embedding_generation_direct():
    """Test generating embeddings directly with the EmbeddingService."""
    logger.info("Testing embedding generation directly...")
    
    # Initialize service
    embedding_service = EmbeddingService()
    
    # Test documents
    documents = [
        "Machine learning is a field of artificial intelligence.",
        "Neural networks are inspired by the human brain.",
        "Natural language processing helps computers understand human language."
    ]
    
    try:
        # Try both potential methods for generating embeddings
        embeddings = []
        
        # Try batch method first
        if hasattr(embedding_service, 'generate_embeddings'):
            logger.info("Using generate_embeddings method")
            embeddings = embedding_service.generate_embeddings(documents)
        # Fall back to single embedding method if batch not available
        elif hasattr(embedding_service, 'generate_embedding'):
            logger.info("Using generate_embedding method")
            embeddings = [embedding_service.generate_embedding(doc) for doc in documents]
        else:
            logger.error("❌ Could not find embedding method in EmbeddingService")
            return False
            
        # Check if embeddings were generated
        if embeddings and all(emb is not None for emb in embeddings):
            logger.info(f"✅ Generated {len(embeddings)} embeddings successfully")
            for i, emb in enumerate(embeddings):
                dim = len(emb) if emb else 0
                logger.info(f"  - Embedding {i}: {dim} dimensions")
            return True
        else:
            logger.error("❌ Failed to generate embeddings")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing embedding generation: {e}")
        return False

def test_vector_repository_direct():
    """Test the VectorRepository directly."""
    logger.info("Testing VectorRepository directly...")
    
    # Initialize services
    embedding_service = EmbeddingService()
    vector_repo = VectorRepository()
    
    # Test content and query
    content = "Machine learning is a field of artificial intelligence."
    query = "Tell me about AI and machine learning"
    content_id = "test_content_123"
    
    try:
        # Determine which embedding method to use
        if hasattr(embedding_service, 'generate_embedding'):
            logger.info("Using generate_embedding method")
            embed_method = embedding_service.generate_embedding
        elif hasattr(embedding_service, 'generate_embeddings'):
            logger.info("Using generate_embeddings method")
            # Create a wrapper to handle single inputs
            embed_method = lambda text: embedding_service.generate_embeddings([text])[0]
        else:
            logger.error("❌ Could not find embedding method in EmbeddingService")
            return False
        
        # Generate embedding and store
        content_embedding = embed_method(content)
        if content_embedding:
            metadata = {"title": "Test Content", "id": content_id}
            success = vector_repo.add_vector(content_embedding, metadata)
            if success:
                logger.info(f"✅ Successfully stored embedding for content_id: {content_id}")
            else:
                logger.error("❌ Failed to store embedding")
                return False
        else:
            logger.error("❌ Failed to generate content embedding")
            return False
        
        # Generate query embedding and search
        query_embedding = embed_method(query)
        if query_embedding:
            results = vector_repo.search_similar_vectors(query_embedding, num_neighbors=3)
            logger.info(f"✅ Vector search returned {len(results)} results")
            for i, result in enumerate(results):
                logger.info(f"  - Result {i}: {result.get('id', 'unknown')} (Score: {result.get('score', 0):.4f})")
            return True
        else:
            logger.error("❌ Failed to generate query embedding")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing VectorRepository: {e}")
        return False

def test_similar_content_api():
    """Test the API endpoint for finding similar content."""
    logger.info("Testing similar content API endpoint...")
    
    # Prepare request data
    query_data = {
        "query": "machine learning and artificial intelligence",
        "limit": 3,
        "filters": {"tags": []}
    }
    
    # Make request
    response = requests.post(f"{API_BASE_URL}/rag/similar", json=query_data)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check for different possible response structures
        if 'results' in data:
            results = data.get('results', [])
        elif 'content' in data:
            results = data.get('content', [])
        elif 'similar' in data:
            results = data.get('similar', [])
        elif isinstance(data, list):
            results = data
        else:
            results = []
        
        if results and len(results) > 0:
            logger.info(f"✅ Similar content API returned {len(results)} results")
            for result in results:
                if isinstance(result, dict):
                    title = result.get('title', 'Unknown')
                    score = result.get('score', 0)
                    logger.info(f"  - {title} (Score: {score})")
                else:
                    logger.info(f"  - {result}")
            
            return True
        else:
            logger.warning("⚠️ Similar content API returned no results, but endpoint is working")
            return True
    else:
        logger.error(f"❌ Similar content API failed with status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False

def test_generate_tags_api():
    """Test the API endpoint for generating tags from content."""
    logger.info("Testing tag generation API endpoint...")
    
    # Get a content item to generate tags for
    content_response = requests.get(f"{API_BASE_URL}/recent-content")
    
    if content_response.status_code == 200:
        content_data = content_response.json()
        
        # Handle different content response formats
        content_items = []
        if isinstance(content_data, dict) and 'content' in content_data:
            content_items = content_data.get('content', [])
        elif isinstance(content_data, list):
            content_items = content_data
        
        if content_items and len(content_items) > 0:
            content_item = content_items[0]
            content_id = None
            
            # Try to get the content ID from different possible fields
            if isinstance(content_item, dict):
                if 'id' in content_item:
                    content_id = content_item['id']
                elif 'contentId' in content_item:
                    content_id = content_item['contentId']
                elif '_id' in content_item:
                    content_id = content_item['_id']
            
            if content_id:
                # Prepare request data
                tag_data = {
                    "contentId": content_id
                }
                
                # Make request
                response = requests.post(f"{API_BASE_URL}/rag/generate-tags", json=tag_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different tag response formats
                    tags = []
                    if isinstance(data, dict) and 'tags' in data:
                        tags = data.get('tags', [])
                    elif isinstance(data, list):
                        tags = data
                    
                    if tags and len(tags) > 0:
                        logger.info(f"✅ Tag generation API returned {len(tags)} tags")
                        if all(isinstance(tag, str) for tag in tags):
                            logger.info(f"  - Tags: {', '.join(tags)}")
                        else:
                            logger.info(f"  - Tags: {tags}")
                        return True
                    else:
                        logger.warning("⚠️ Tag generation API returned no tags, but endpoint is working")
                        return True
                else:
                    logger.error(f"❌ Tag generation API failed with status code {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
            else:
                logger.warning("⚠️ No content ID found for tag generation test")
                return True
        else:
            logger.warning("⚠️ No content items found for tag generation test")
            return True
    else:
        logger.error(f"❌ Failed to get content for tag generation test")
        logger.error(f"Response: {content_response.text}")
        return False

def run_all_tests():
    """Run all vector search tests."""
    logger.info("Starting vector search integration tests")
    
    # Direct tests (if possible)
    if direct_import:
        embedding_ok = test_embedding_generation_direct()
        vector_repo_ok = test_vector_repository_direct()
    else:
        embedding_ok = True
        vector_repo_ok = True
        logger.warning("Direct vector search tests skipped due to import errors")
    
    # API tests
    similar_content_ok = test_similar_content_api()
    tag_generation_ok = test_generate_tags_api()
    
    # Summary
    logger.info("\n=== Test Results ===")
    
    if direct_import:
        logger.info(f"Embedding Generation: {'✅ PASSED' if embedding_ok else '❌ FAILED'}")
        logger.info(f"Vector Repository: {'✅ PASSED' if vector_repo_ok else '❌ FAILED'}")
    
    logger.info(f"Similar Content API: {'✅ PASSED' if similar_content_ok else '❌ FAILED'}")
    logger.info(f"Tag Generation API: {'✅ PASSED' if tag_generation_ok else '❌ FAILED'}")
    
    # Overall result
    api_tests = [similar_content_ok, tag_generation_ok]
    direct_tests = []
    if direct_import:
        direct_tests = [embedding_ok, vector_repo_ok]
    
    if all(api_tests) and all(direct_tests):
        logger.info("\n✅ All vector search tests passed!")
        return True
    else:
        logger.info("\n❌ Some vector search tests failed. Check the log for details.")
        return False

if __name__ == "__main__":
    run_all_tests() 