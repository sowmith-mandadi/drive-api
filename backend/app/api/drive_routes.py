"""Google Drive integration routes for the API."""

from flask import Blueprint, request, jsonify
import logging
import os
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.services.content_service import ContentService

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
drive_bp = Blueprint('drive', __name__, url_prefix='/api/drive')

# Initialize services
content_service = ContentService()

# Initialize Google Drive API
def get_drive_service():
    """Get an authorized Google Drive API service."""
    try:
        # First check if we're running in Cloud Shell with environment variables
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            logger.info(f"Using environment variables for Google Drive API with project: {project_id}")
            
            # Use default credentials in Cloud Shell
            return build('drive', 'v3', cache_discovery=False)
        
        # If not in Cloud Shell, try to use credentials file
        if os.path.exists('credentials.json'):
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            return build('drive', 'v3', credentials=credentials)
        else:
            logger.warning("Credentials file not found. Running Drive API in limited mode.")
            return build('drive', 'v3', cache_discovery=False)
    except Exception as e:
        logger.error(f"Error initializing Drive service: {e}")
        return None

@drive_bp.route('/files/<file_id>', methods=['GET'])
def get_file_metadata(file_id):
    """Get metadata for a Google Drive file."""
    try:
        logger.info(f"Getting metadata for Drive file {file_id}")
        drive_service = get_drive_service()
        
        if not drive_service:
            return jsonify({"error": "Could not initialize Drive service"}), 500
        
        file = drive_service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,webViewLink,iconLink,thumbnailLink"
        ).execute()
        
        return jsonify(file)
    except Exception as e:
        logger.error(f"Error getting Drive file metadata: {e}")
        return jsonify({
            "error": f"Failed to get file metadata: {str(e)}",
            "id": file_id,
            "name": "Unknown file",
            "mimeType": "application/octet-stream",
            "webViewLink": f"https://drive.google.com/file/d/{file_id}/view"
        }), 500

@drive_bp.route('/import', methods=['POST'])
def import_drive_files():
    """Import files from Google Drive."""
    try:
        logger.info("Received Drive import request")
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        file_ids = data.get('fileIds', [])
        metadata = data.get('metadata', {})
        content_id = metadata.get('contentId')
        
        if not file_ids:
            return jsonify({"error": "No file IDs provided"}), 400
        
        logger.info(f"Importing {len(file_ids)} Drive files")
        
        # Process Google Drive files
        drive_service = get_drive_service()
        
        if not drive_service:
            return jsonify({"error": "Could not initialize Drive service"}), 500
        
        # Download and process files
        result = content_service.process_drive_content(drive_service, file_ids, metadata)
        
        logger.info("Drive import successful")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error importing Drive files: {e}")
        return jsonify({"error": str(e), "success": False}), 500 