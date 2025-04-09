"""
Tests for the RAG API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

# Helper function to create test content
def create_test_content():
    """Create test content for RAG testing."""
    test_content = {
        "title": "RAG Test Content",
        "description": "This is a test content for RAG",
        "content_type": "text",
        "source": "upload",
        "tags": json.dumps(["test", "rag"]),
        "metadata": json.dumps({"test_key": "test_value"}),
        "extracted_text": "This is some extracted text for testing RAG capabilities."
    }
    
    response = client.post("/api/content/", data=test_content)
    return response.json()["id"]

def test_ask_question():
    """Test asking a question with RAG."""
    # Create test content
    content_id = create_test_content()
    
    # Ask a question
    question_data = {
        "question": "What is this content about?",
        "content_ids": [content_id]
    }
    
    response = client.post("/api/rag/ask", json=question_data)
    assert response.status_code == 200
    result = response.json()
    assert "answer" in result
    assert "sources" in result
    assert "model_used" in result
    
    # Clean up
    client.delete(f"/api/content/{content_id}")

def test_summarize_content():
    """Test content summarization."""
    # Create test content
    content_id = create_test_content()
    
    # Generate summary
    response = client.post(f"/api/rag/{content_id}/summarize")
    assert response.status_code == 200
    result = response.json()
    assert "content_id" in result
    assert "summary" in result
    assert result["content_id"] == content_id
    
    # Clean up
    client.delete(f"/api/content/{content_id}")

def test_generate_tags():
    """Test tag generation."""
    # Create test content
    content_id = create_test_content()
    
    # Generate tags
    response = client.post(f"/api/rag/{content_id}/tags")
    assert response.status_code == 200
    result = response.json()
    assert "content_id" in result
    assert "tags" in result
    assert result["content_id"] == content_id
    assert isinstance(result["tags"], list)
    
    # Clean up
    client.delete(f"/api/content/{content_id}")

def test_find_similar_content():
    """Test finding similar content."""
    # Create test content
    content_id = create_test_content()
    
    # Find similar content
    response = client.get(f"/api/rag/{content_id}/similar")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    
    # Check structure of results
    if len(results) > 0:
        assert "id" in results[0]
        assert "title" in results[0]
        assert "similarity_score" in results[0]
    
    # Clean up
    client.delete(f"/api/content/{content_id}")

def test_nonexistent_content():
    """Test RAG endpoints with nonexistent content ID."""
    nonexistent_id = "nonexistent-id"
    
    # Test summarize
    response = client.post(f"/api/rag/{nonexistent_id}/summarize")
    assert response.status_code == 404
    
    # Test tags
    response = client.post(f"/api/rag/{nonexistent_id}/tags")
    assert response.status_code == 404
    
    # Test similar
    response = client.get(f"/api/rag/{nonexistent_id}/similar")
    assert response.status_code == 404

# Run tests with: pytest tests/test_rag_api.py -v 