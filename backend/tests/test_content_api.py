"""
Tests for the content API endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

def test_list_content():
    """Test listing content."""
    response = client.get("/api/content/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_and_get_content():
    """Test creating and getting content."""
    # Create test content
    test_content = {
        "title": "Test Content",
        "description": "This is a test content",
        "content_type": "text",
        "source": "upload",
        "tags": json.dumps(["test", "api"]),
        "metadata": json.dumps({"test_key": "test_value"})
    }
    
    response = client.post("/api/content/", data=test_content)
    assert response.status_code == 200
    created_content = response.json()
    assert created_content["title"] == "Test Content"
    content_id = created_content["id"]
    
    # Get the created content
    response = client.get(f"/api/content/{content_id}")
    assert response.status_code == 200
    fetched_content = response.json()
    assert fetched_content["id"] == content_id
    assert fetched_content["title"] == "Test Content"
    
    # Clean up - delete the content
    response = client.delete(f"/api/content/{content_id}")
    assert response.status_code == 200

def test_update_content():
    """Test updating content."""
    # Create test content
    test_content = {
        "title": "Update Test",
        "description": "This will be updated",
        "content_type": "text",
        "source": "upload",
        "tags": json.dumps(["test"]),
        "metadata": json.dumps({})
    }
    
    response = client.post("/api/content/", data=test_content)
    assert response.status_code == 200
    content_id = response.json()["id"]
    
    # Update the content
    update_data = {
        "title": "Updated Title",
        "description": "This has been updated",
        "tags": ["test", "updated"]
    }
    
    response = client.put(f"/api/content/{content_id}", json=update_data)
    assert response.status_code == 200
    updated_content = response.json()
    assert updated_content["title"] == "Updated Title"
    assert updated_content["description"] == "This has been updated"
    assert "updated" in updated_content["tags"]
    
    # Clean up
    response = client.delete(f"/api/content/{content_id}")
    assert response.status_code == 200

def test_search_content():
    """Test searching content."""
    # Create test content items
    test_content1 = {
        "title": "Search Test 1",
        "description": "First search test",
        "content_type": "text",
        "source": "upload",
        "tags": json.dumps(["search", "test1"]),
        "metadata": json.dumps({"category": "testing"})
    }
    
    test_content2 = {
        "title": "Search Test 2",
        "description": "Second search test with special word: searchme",
        "content_type": "text",
        "source": "upload",
        "tags": json.dumps(["search", "test2"]),
        "metadata": json.dumps({"category": "testing"})
    }
    
    response1 = client.post("/api/content/", data=test_content1)
    response2 = client.post("/api/content/", data=test_content2)
    assert response1.status_code == 200
    assert response2.status_code == 200
    content_id1 = response1.json()["id"]
    content_id2 = response2.json()["id"]
    
    # Search by query
    search_data = {"query": "searchme"}
    response = client.post("/api/content/search", json=search_data)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(item["title"] == "Search Test 2" for item in results)
    
    # Search by filter
    filter_data = {"filters": {"tags": ["test1"]}}
    response = client.post("/api/content/search", json=filter_data)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(item["title"] == "Search Test 1" for item in results)
    
    # Clean up
    client.delete(f"/api/content/{content_id1}")
    client.delete(f"/api/content/{content_id2}")

# Run tests with: pytest tests/test_content_api.py -v 