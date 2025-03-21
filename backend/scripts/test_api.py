"""
Test script for validating API endpoints.
This script will test each endpoint of the API to ensure it's working correctly.
"""

import requests
import json
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings
from config.settings import get_config

# Get configuration
config = get_config()

# Set API base URL - default to localhost:3000 if not set
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health endpoint working!")
        return True
    else:
        print(f"❌ Health endpoint failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_rag_endpoints():
    """Test the RAG API endpoints."""
    print("\nTesting RAG endpoints...")
    
    # Test /rag/ask endpoint
    print("Testing /rag/ask endpoint...")
    ask_data = {
        "question": "What is machine learning?",
        "contentIds": [],
        "filters": {"tracks": [], "tags": []}
    }
    response = requests.post(f"{API_BASE_URL}/rag/ask", json=ask_data)
    if response.status_code == 200:
        print("✅ RAG /ask endpoint working!")
        print(f"Response preview: {response.json().get('answer', '')[:100]}...")
    else:
        print(f"❌ RAG /ask endpoint failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # More RAG endpoint tests can be added here
    
    return True

def test_content_endpoints():
    """Test the Content API endpoints."""
    print("\nTesting Content endpoints...")
    
    # Test /recent-content endpoint
    print("Testing /recent-content endpoint...")
    response = requests.get(f"{API_BASE_URL}/recent-content")
    if response.status_code == 200:
        print("✅ Content /recent-content endpoint working!")
        content_data = response.json()
        content_count = len(content_data.get("content", []))
        print(f"Retrieved {content_count} content items.")
    else:
        print(f"❌ Content /recent-content endpoint failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # More content endpoint tests can be added here
    
    return True

def run_all_tests():
    """Run all API tests."""
    print(f"Testing API at {API_BASE_URL}")
    
    # Run tests
    health_ok = test_health_endpoint()
    rag_ok = test_rag_endpoints()
    content_ok = test_content_endpoints()
    
    # Summary
    print("\n=== Test Results ===")
    print(f"Health API: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    print(f"RAG API: {'✅ PASSED' if rag_ok else '❌ FAILED'}")
    print(f"Content API: {'✅ PASSED' if content_ok else '❌ FAILED'}")
    
    # Overall result
    if all([health_ok, rag_ok, content_ok]):
        print("\n✅ All tests passed! API is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the log for details.")
        return False

if __name__ == "__main__":
    run_all_tests() 