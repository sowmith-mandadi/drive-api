"""
Tests for the Google Drive API endpoints.
"""
from unittest.mock import patch

import pytest

from app.services.drive_service import DriveService


def test_list_drive_files(mock_drive_service, authenticated_client):
    """Test listing files from Google Drive."""
    response = authenticated_client.get("/api/drive/files")
    assert response.status_code == 200

    # Verify response content
    files = response.json()
    assert isinstance(files, list)
    assert len(files) > 0
    assert "id" in files[0]
    assert "name" in files[0]
    assert "mimeType" in files[0]


def test_get_drive_file(mock_drive_service, authenticated_client):
    """Test getting a specific file from Google Drive."""
    file_id = "test-file-1"
    response = authenticated_client.get(f"/api/drive/files/{file_id}")
    assert response.status_code == 200

    # Verify file details
    file_data = response.json()
    assert file_data["id"] == file_id
    assert file_data["name"] == "Test File 1.pdf"
    assert "webViewLink" in file_data


def test_drive_files_unauthenticated(client):
    """Test that Drive endpoints require authentication."""
    response = client.get("/api/drive/files")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@patch("app.services.drive_service.DriveService.import_files")
def test_import_drive_files(mock_import, authenticated_client):
    """Test importing files from Google Drive."""
    # Setup mock for import_files
    mock_import.return_value = [
        {
            "id": "imported-1",
            "title": "Imported File 1",
            "description": "Imported from Drive",
            "source": "drive",
        }
    ]

    # Test import endpoint
    import_data = {"file_ids": ["test-file-1", "test-file-2"], "import_text": True}

    response = authenticated_client.post("/api/drive/import", json=import_data)
    assert response.status_code == 200

    # Verify the response
    imported_files = response.json()
    assert isinstance(imported_files, list)
    assert len(imported_files) > 0
    assert imported_files[0]["source"] == "drive"

    # Verify the import_files was called with correct params
    mock_import.assert_called_once_with(
        file_ids=import_data["file_ids"], import_text=import_data["import_text"]
    )


def test_drive_file_not_found(mock_drive_service, authenticated_client):
    """Test handling of non-existent file."""
    # Mock the service to raise an exception for non-existent file
    with patch("app.services.drive_service.DriveService.get_file_metadata") as mock_get:
        mock_get.side_effect = Exception("File not found")

        response = authenticated_client.get("/api/drive/files/nonexistent-id")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]


@pytest.mark.integration
def test_drive_service_integration():
    """Integration test for DriveService (requires actual credentials)."""
    # This would be marked to skip in CI/CD environments
    pytest.skip("Integration test requires actual Google credentials")

    # In a real test, we'd use actual credentials and test with real Drive API
    service = DriveService(credentials={"token": "real-token"})
    files = service.list_files(query="name contains 'Test'")
    assert isinstance(files, list)


@pytest.mark.parametrize(
    "mime_type,expected_type",
    [
        ("application/pdf", "pdf"),
        ("application/vnd.google-apps.document", "document"),
        ("application/vnd.google-apps.spreadsheet", "spreadsheet"),
        ("application/vnd.google-apps.presentation", "presentation"),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
        ("image/jpeg", "image"),
        ("unknown/type", "other"),
    ],
)
def test_drive_mime_type_categorization(
    mime_type, expected_type, authenticated_client, mock_drive_service
):
    """Test that Drive API correctly categorizes different MIME types."""
    # Mock the drive service to return our specific mime type
    with patch("app.services.drive_service.build_drive_service") as mock_build:
        mock_service = mock_build.return_value
        mock_files_list = mock_service.files.return_value.list.return_value.execute
        mock_files_list.return_value = {
            "files": [{"id": "test-file-mime", "name": "Test MIME File", "mimeType": mime_type}]
        }

        response = authenticated_client.get("/api/drive/files")
        assert response.status_code == 200
        files = response.json()

        assert len(files) > 0
        assert files[0]["contentType"] == expected_type


# Performance test for drive API
@pytest.mark.performance
def test_drive_files_performance(authenticated_client, mock_drive_service):
    """Test performance of drive files endpoint."""
    import time

    # Measure response time
    start_time = time.time()
    response = authenticated_client.get("/api/drive/files")
    end_time = time.time()

    assert response.status_code == 200

    # API should respond within reasonable time (less than 500ms)
    response_time = end_time - start_time
    assert response_time < 0.5, f"Response time too slow: {response_time}s"


# Run tests with: pytest tests/test_drive_api.py -v
