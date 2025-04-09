"""
Performance tests for the API endpoints.

These tests measure the response time and performance characteristics of various API endpoints.
They are marked with the 'performance' marker and can be run selectively with:
pytest -m performance
"""
import time

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestEndpointPerformance:
    """Performance tests for API endpoints."""

    @pytest.mark.performance
    @pytest.mark.parametrize(
        "endpoint", ["/api/health", "/api/health/info", "/api/content/", "/api/auth/status"]
    )
    def test_endpoint_response_time(self, endpoint):
        """Test that endpoints respond within acceptable time limits."""
        # Make the request and time it
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()

        # Calculate response time
        response_time = end_time - start_time

        # Log the response time
        print(f"\nEndpoint {endpoint} response time: {response_time:.4f}s")

        # Check that the response was successful
        assert response.status_code == 200

        # Different endpoints have different performance requirements
        if endpoint == "/api/health":
            # Health checks should be extremely fast
            assert response_time < 0.05, f"Health check too slow: {response_time:.4f}s"
        elif endpoint == "/api/content/":
            # Content listing might need to query database
            assert response_time < 0.5, f"Content listing too slow: {response_time:.4f}s"
        else:
            # Other endpoints should still be reasonably fast
            assert response_time < 0.2, f"Endpoint {endpoint} too slow: {response_time:.4f}s"


class TestContentAPIPerformance:
    """Performance tests specifically for content API operations."""

    @pytest.fixture
    def setup_test_content(self):
        """Create multiple test content items for performance testing."""
        # Create 10 test content items
        content_ids = []
        for i in range(10):
            test_content = {
                "title": f"Performance Test Content {i}",
                "description": f"Content for performance testing {i}",
                "content_type": "text",
                "source": "test",
                "tags": f'["performance", "test{i}"]',
                "metadata": f'{{"test_number": {i}}}',
            }

            response = client.post("/api/content/", data=test_content)
            assert response.status_code == 200
            content_ids.append(response.json()["id"])

        yield content_ids

        # Clean up all created content
        for content_id in content_ids:
            client.delete(f"/api/content/{content_id}")

    @pytest.mark.performance
    def test_content_search_performance(self, setup_test_content):
        """Test performance of content search endpoint."""
        # Search by query
        search_data = {"query": "performance"}

        start_time = time.time()
        response = client.post("/api/content/search", json=search_data)
        end_time = time.time()

        search_time = end_time - start_time
        print(f"\nContent search time: {search_time:.4f}s")

        assert response.status_code == 200
        assert search_time < 0.5, f"Content search too slow: {search_time:.4f}s"

        # Search by tag filter
        filter_data = {"filters": {"tags": ["performance"]}}

        start_time = time.time()
        response = client.post("/api/content/search", json=filter_data)
        end_time = time.time()

        filter_time = end_time - start_time
        print(f"Content filter time: {filter_time:.4f}s")

        assert response.status_code == 200
        assert filter_time < 0.5, f"Content filtering too slow: {filter_time:.4f}s"

    @pytest.mark.performance
    def test_content_crud_performance(self):
        """Test performance of content CRUD operations."""
        # Create
        test_content = {
            "title": "Performance CRUD Test",
            "description": "Testing CRUD performance",
            "content_type": "text",
            "source": "test",
            "tags": '["performance", "crud"]',
            "metadata": '{"test": true}',
        }

        start_time = time.time()
        response = client.post("/api/content/", data=test_content)
        create_time = time.time() - start_time

        assert response.status_code == 200
        content_id = response.json()["id"]
        print(f"\nContent creation time: {create_time:.4f}s")
        assert create_time < 0.5, f"Content creation too slow: {create_time:.4f}s"

        # Read
        start_time = time.time()
        response = client.get(f"/api/content/{content_id}")
        read_time = time.time() - start_time

        assert response.status_code == 200
        print(f"Content read time: {read_time:.4f}s")
        assert read_time < 0.1, f"Content read too slow: {read_time:.4f}s"

        # Update
        update_data = {
            "title": "Updated Performance CRUD Test",
            "description": "Updated description",
        }

        start_time = time.time()
        response = client.put(f"/api/content/{content_id}", json=update_data)
        update_time = time.time() - start_time

        assert response.status_code == 200
        print(f"Content update time: {update_time:.4f}s")
        assert update_time < 0.5, f"Content update too slow: {update_time:.4f}s"

        # Delete
        start_time = time.time()
        response = client.delete(f"/api/content/{content_id}")
        delete_time = time.time() - start_time

        assert response.status_code == 200
        print(f"Content deletion time: {delete_time:.4f}s")
        assert delete_time < 0.5, f"Content deletion too slow: {delete_time:.4f}s"


@pytest.mark.performance
def test_api_memory_usage():
    """
    Test memory usage pattern for multiple API calls.

    This is a simple test that makes multiple requests to the API
    and checks that we don't have obvious memory leaks.
    A more thorough test would require proper profiling tools.
    """
    import resource

    # Get initial memory usage
    initial_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    # Make multiple requests to different endpoints
    endpoints = ["/api/health", "/api/content/", "/api/auth/status"]
    for _ in range(50):  # Make 50 requests to each endpoint
        for endpoint in endpoints:
            client.get(endpoint)

    # Get final memory usage
    final_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_increase = final_usage - initial_usage

    print(f"\nMemory usage increased by: {memory_increase} KB")
    # Check for large memory increases that might indicate a leak
    # This threshold needs to be adjusted based on the specific application
    assert memory_increase < 10000, f"Potential memory leak: {memory_increase} KB increase"
