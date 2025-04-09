"""
End-to-end tests for the Conference CMS API.

These tests verify complete workflows across multiple API endpoints,
simulating real user interactions with the system.
"""
import json
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.e2e
class TestContentManagementWorkflow:
    """
    End-to-end tests for content management workflows.
    Tests the complete lifecycle of content in the system.
    """

    def test_content_lifecycle(self):
        """Test the full content lifecycle: create, read, update, search, delete."""
        client = TestClient(app)

        # 1. Create content
        test_content = {
            "title": "E2E Test Content",
            "description": "Testing the full content lifecycle",
            "content_type": "text",
            "source": "manual",
            "tags": json.dumps(["e2e", "test", "lifecycle"]),
            "metadata": json.dumps({"importance": "high", "status": "active"}),
        }

        response = client.post("/api/content/", data=test_content)
        assert response.status_code == 200
        created_content = response.json()
        content_id = created_content["id"]

        # 2. Retrieve content by ID
        response = client.get(f"/api/content/{content_id}")
        assert response.status_code == 200
        fetched_content = response.json()
        assert fetched_content["id"] == content_id
        assert fetched_content["title"] == "E2E Test Content"
        assert "e2e" in fetched_content["tags"]

        # 3. Update content
        update_data = {
            "title": "Updated E2E Test Content",
            "description": "Updated description for E2E test",
            "tags": ["e2e", "test", "updated"],
        }

        response = client.put(f"/api/content/{content_id}", json=update_data)
        assert response.status_code == 200
        updated_content = response.json()
        assert updated_content["title"] == "Updated E2E Test Content"
        assert "updated" in updated_content["tags"]

        # 4. Search for content
        # By query
        search_query = {"query": "e2e test"}
        response = client.post("/api/content/search", json=search_query)
        assert response.status_code == 200
        search_results = response.json()
        assert any(c["id"] == content_id for c in search_results)

        # By tag filter
        filter_query = {"filters": {"tags": ["e2e"]}}
        response = client.post("/api/content/search", json=filter_query)
        assert response.status_code == 200
        filter_results = response.json()
        assert any(c["id"] == content_id for c in filter_results)

        # 5. Delete content
        response = client.delete(f"/api/content/{content_id}")
        assert response.status_code == 200

        # 6. Verify deletion
        response = client.get(f"/api/content/{content_id}")
        assert response.status_code == 404


@pytest.mark.e2e
class TestFileUploadWorkflow:
    """
    End-to-end tests for file upload workflows.
    """

    def test_file_upload_processing(self):
        """Test uploading a file, processing it, and retrieving the processed content."""
        client = TestClient(app)

        # Create a temporary text file for testing
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is test content for the file upload E2E test.\n")
            temp_file.write(
                b"It should be processed and stored in the content management system.\n"
            )
            temp_file_path = temp_file.name

        try:
            # 1. Upload file with metadata
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test_upload.txt", f, "text/plain")}
                data = {
                    "title": "Uploaded Test File",
                    "description": "File uploaded during E2E test",
                    "content_type": "text",
                    "source": "upload",
                    "tags": json.dumps(["e2e", "upload", "file"]),
                    "metadata": json.dumps({"file_type": "text"}),
                }

                response = client.post("/api/content/upload", files=files, data=data)
                assert response.status_code == 200
                uploaded_content = response.json()
                content_id = uploaded_content["id"]

                # 2. Verify file was processed correctly
                response = client.get(f"/api/content/{content_id}")
                assert response.status_code == 200
                content = response.json()
                assert content["title"] == "Uploaded Test File"
                assert "upload" in content["tags"]
                assert content["source"] == "upload"
                assert "extracted_text" in content or "file_path" in content

                # 3. Clean up
                response = client.delete(f"/api/content/{content_id}")
                assert response.status_code == 200

        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


@pytest.mark.e2e
class TestDriveIntegrationWorkflow:
    """
    End-to-end tests for Google Drive integration.
    Uses mocks for the external Google Drive API calls.
    """

    @patch("app.services.drive_service.DriveService.get_file_content")
    @patch("app.services.drive_service.DriveService.import_files")
    def test_drive_import_workflow(
        self, mock_import_files, mock_get_file_content, authenticated_client
    ):
        """Test the workflow for importing files from Google Drive."""
        # Mock the drive import to return dummy content
        mock_import_files.return_value = [
            {
                "id": "drive-content-1",
                "title": "Drive File 1",
                "description": "Imported from Drive during E2E test",
                "content_type": "document",
                "source": "drive",
                "tags": ["drive", "e2e", "test"],
                "metadata": {
                    "drive_id": "test-drive-id-1",
                    "mime_type": "application/vnd.google-apps.document",
                },
            }
        ]

        # Mock file content
        mock_get_file_content.return_value = "This is test content from a Google Drive file."

        # 1. List Drive files
        response = authenticated_client.get("/api/drive/files")
        assert response.status_code == 200
        files = response.json()
        assert len(files) > 0
        drive_file_id = files[0]["id"]

        # 2. Import files from Drive
        import_data = {"file_ids": [drive_file_id], "import_text": True}

        response = authenticated_client.post("/api/drive/import", json=import_data)
        assert response.status_code == 200
        imported_files = response.json()
        assert len(imported_files) > 0
        content_id = imported_files[0]["id"]

        # 3. Check the imported content
        response = authenticated_client.get(f"/api/content/{content_id}")
        assert response.status_code == 200
        content = response.json()
        assert content["source"] == "drive"
        assert "drive" in content["tags"]

        # 4. Clean up
        response = authenticated_client.delete(f"/api/content/{content_id}")
        assert response.status_code == 200


@pytest.mark.e2e
class TestRAGWorkflow:
    """
    End-to-end tests for RAG (Retrieval Augmented Generation) workflows.
    """

    @patch("app.services.rag_service.RAGService.generate_answer")
    def test_question_answer_workflow(self, mock_generate_answer, authenticated_client):
        """Test the complete question-answering workflow."""
        # Create test content
        test_content = {
            "title": "RAG Test Content",
            "description": "Content for testing RAG workflows",
            "content_type": "text",
            "source": "manual",
            "tags": json.dumps(["rag", "e2e", "test"]),
            "metadata": json.dumps({"test": True}),
            "extracted_text": "This is test content for RAG. It contains information about testing.",
        }

        response = authenticated_client.post("/api/content/", data=test_content)
        content_id = response.json()["id"]

        # Mock the RAG answer generation
        mock_generate_answer.return_value = {
            "answer": "This content is about testing RAG capabilities.",
            "sources": [content_id],
            "model_used": "test-model",
        }

        # 1. Ask a question
        question_data = {"question": "What is this content about?", "content_ids": [content_id]}

        response = authenticated_client.post("/api/rag/ask", json=question_data)
        assert response.status_code == 200
        rag_response = response.json()
        assert "answer" in rag_response
        assert "sources" in rag_response
        assert content_id in rag_response["sources"]

        # 2. Generate a summary
        with patch("app.services.rag_service.RAGService.generate_summary") as mock_summary:
            mock_summary.return_value = "This is a test summary of RAG content."

            response = authenticated_client.post(f"/api/rag/{content_id}/summarize")
            assert response.status_code == 200
            summary_response = response.json()
            assert "summary" in summary_response
            assert summary_response["content_id"] == content_id

        # 3. Generate tags
        with patch("app.services.rag_service.RAGService.generate_tags") as mock_tags:
            mock_tags.return_value = ["rag", "testing", "ai", "generated"]

            response = authenticated_client.post(f"/api/rag/{content_id}/tags")
            assert response.status_code == 200
            tags_response = response.json()
            assert "tags" in tags_response
            assert "generated" in tags_response["tags"]

        # 4. Clean up
        response = authenticated_client.delete(f"/api/content/{content_id}")
        assert response.status_code == 200
