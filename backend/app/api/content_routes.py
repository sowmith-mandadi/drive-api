"""Content management routes for the API."""

from flask import Blueprint, request, jsonify
import logging
from app.services.content_service import ContentService

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
content_bp = Blueprint('content', __name__)

# Initialize services
content_service = ContentService()

@content_bp.route('/upload', methods=['POST', 'OPTIONS'])
def upload_content():
    """Upload conference content with metadata."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        logger.info("Received upload request")
        
        # Process form data
        title = request.form.get('title')
        description = request.form.get('description', '')
        track = request.form.get('track', '')
        tags = request.form.get('tags', '')
        session_type = request.form.get('session_type', '')
        presenters = request.form.get('presenters', '')
        slide_url = request.form.get('slide_url', '')
        drive_link = request.form.get('drive_link', '')
        
        # Parse lists
        tags_list = tags.split(",") if tags else []
        presenters_list = presenters.split(",") if presenters else []
        
        # Create metadata object
        metadata = {
            "title": title,
            "description": description,
            "track": track,
            "tags": tags_list,
            "session_type": session_type,
            "presenters": presenters_list,
            "slide_url": slide_url,
            "drive_link": drive_link
        }
        
        # Check if files were uploaded
        files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            logger.info(f"Received {len(files)} files")
        
        # Process the content
        result = content_service.process_content(files, metadata)
        
        # Add CORS headers to the response
        logger.info("Upload successful, returning response")
        resp = jsonify(result)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/content-by-ids', methods=['POST'])
def get_content_by_ids():
    """Get multiple content items by their IDs."""
    try:
        data = request.json
        content_ids = data.get('ids', [])
        
        if not content_ids:
            return jsonify({"error": "No content IDs provided"}), 400
        
        contents = content_service.get_content_by_ids(content_ids)
        
        return jsonify(contents)
    except Exception as e:
        logger.error(f"Error fetching content by IDs: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/popular-tags', methods=['GET'])
def get_popular_tags():
    """Get most popular tags."""
    try:
        limit = int(request.args.get('limit', 20))
        
        tags = content_service.get_popular_tags(limit)
        
        return jsonify(tags)
    except Exception as e:
        logger.error(f"Error fetching popular tags: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/recent-content', methods=['GET'])
def get_recent_content():
    """Get recent content with pagination."""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        result = content_service.get_recent_content(page, page_size)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching recent content: {e}")
        return jsonify({"error": str(e)}), 500 