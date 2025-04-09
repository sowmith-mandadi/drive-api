"""
Locust load testing file for Conference CMS API.

To run:
    locust -f tests/locustfile.py --host=http://localhost:8000

Then access the Locust web interface at http://localhost:8089
"""
import json
import random

from locust import HttpUser, between, task


class ApiUser(HttpUser):
    """
    Simulates a user interacting with the Conference CMS API.
    """

    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks

    def on_start(self):
        """Called when a user starts."""
        # Check application health to ensure it's running
        self.client.get("/api/health")
        self.content_ids = []  # Store content IDs created by this user

    def on_stop(self):
        """Called when a user stops."""
        # Clean up any content created by this user
        for content_id in self.content_ids:
            self.client.delete(f"/api/content/{content_id}")

    @task(5)
    def get_health(self):
        """Simple health check - high frequency."""
        self.client.get("/api/health")

    @task(2)
    def get_content_list(self):
        """Get content list - medium frequency."""
        self.client.get("/api/content/")

    @task(1)
    def search_content(self):
        """Search content - lower frequency."""
        # Sometimes search by query, sometimes by tag
        if random.choice([True, False]):
            search_data = {"query": random.choice(["test", "content", "conference", "api"])}
        else:
            search_data = {"filters": {"tags": [random.choice(["test", "api", "performance"])]}}

        self.client.post("/api/content/search", json=search_data)

    @task(1)
    def content_lifecycle(self):
        """Complete content lifecycle - low frequency."""
        # Create content
        tags = random.sample(["test", "locust", "load", "api", "performance"], 2)
        test_content = {
            "title": f"Load Test Content {random.randint(1000, 9999)}",
            "description": "Content created during load testing",
            "content_type": "text",
            "source": "test",
            "tags": json.dumps(tags),
            "metadata": json.dumps({"test": True, "load": True}),
        }

        response = self.client.post("/api/content/", data=test_content)
        if response.status_code == 200:
            content_id = response.json()["id"]
            self.content_ids.append(content_id)

            # Get content
            self.client.get(f"/api/content/{content_id}")

            # Update content
            update_data = {
                "title": f"Updated Load Test Content {random.randint(1000, 9999)}",
                "description": "Updated description",
            }
            self.client.put(f"/api/content/{content_id}", json=update_data)

            # Delete content
            self.client.delete(f"/api/content/{content_id}")
            self.content_ids.remove(content_id)


class AuthenticatedApiUser(HttpUser):
    """
    Simulates an authenticated user interacting with protected endpoints.
    Note: In a real test, this would handle actual authentication.
    For load testing purposes, we're simulating authenticated calls.
    """

    wait_time = between(2, 5)  # Authenticated users might do more complex operations

    def on_start(self):
        """Called when a user starts - would handle auth in a real test."""
        # In a real test, we would authenticate here
        # For load testing, we're just setting a mock cookie
        self.client.cookies.set("session", "mock-session-value")

    @task(3)
    def get_drive_files(self):
        """Get Drive files - higher frequency for auth users."""
        with self.client.get("/api/drive/files", catch_response=True) as response:
            # In load testing with mocked auth, we might get 401s
            # We'll mark them as successful for testing purposes
            if response.status_code == 401:
                response.success()

    @task(1)
    def ask_rag_question(self):
        """Ask RAG question - lower frequency."""
        question_data = {
            "question": random.choice(
                [
                    "What is this content about?",
                    "Summarize this document",
                    "What are the key points?",
                    "How does this relate to machine learning?",
                ]
            ),
            "content_ids": ["dummy-content-id"],  # Would use real IDs in actual test
        }

        with self.client.post("/api/rag/ask", json=question_data, catch_response=True) as response:
            # Handle potential 401 or 404 errors in load testing
            if response.status_code in [401, 404]:
                response.success()


# To run:
# locust -f tests/locustfile.py --host=http://localhost:8000
