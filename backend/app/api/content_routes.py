"""Content management routes for the API."""

from flask import Blueprint, request, jsonify
import logging
from app.services.content_service import ContentService

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
content_bp = Blueprint('content', __name__, url_prefix='/api')

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
        
        # Debug request information
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request form keys: {list(request.form.keys()) if request.form else 'No form data'}")
        logger.info(f"Request files keys: {list(request.files.keys()) if request.files else 'No files'}")
        
        # Process form data
        title = request.form.get('title', '')
        if not title:
            logger.warning("No title provided in request")
            title = f"Untitled Upload {logging.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
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
        elif 'file' in request.files:
            # Try singular 'file' as well
            files = request.files.getlist('file')
            logger.info(f"Received {len(files)} files from 'file' field")
        
        # Process the content even if no files were uploaded
        result = content_service.process_content(files, metadata)
        
        # If AI content was generated, include it in the response
        if 'content_id' in result:
            content_id = result['content_id']
            content = content_service.get_content_by_id(content_id)
            
            if content and 'metadata' in content:
                ai_content = {}
                
                # Check for AI summary
                if 'ai_summary' in content['metadata']:
                    ai_content['summary'] = content['metadata']['ai_summary']
                    
                # Check for AI tags
                if 'ai_tags' in content['metadata']:
                    ai_content['tags'] = content['metadata']['ai_tags']
                
                # Add AI content to result if available
                if ai_content:
                    result['aiContent'] = ai_content
        
        # Add CORS headers to the response
        logger.info("Upload successful, returning response")
        resp = jsonify(result)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Return a more user-friendly error response
        return jsonify({
            "error": "Upload failed", 
            "message": str(e),
            "success": False
        }), 500

@content_bp.route('/search', methods=['POST', 'OPTIONS'])
def search_content():
    """Search for content based on query and filters."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        logger.info("Received search request")
        data = request.json
        
        query = data.get('query', '')
        filters = data.get('filters', {})
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)
        
        logger.info(f"Search parameters: query='{query}', filters={filters}, page={page}, page_size={page_size}")
        
        # Call the content service to perform the search
        result = content_service.search_content(query, filters, page, page_size)
        
        # Add CORS headers to the response
        resp = jsonify(result)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/content-by-ids', methods=['POST', 'OPTIONS'])
def get_content_by_ids():
    """Get multiple content items by their IDs."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        data = request.json
        content_ids = data.get('ids', [])
        
        if not content_ids:
            return jsonify({"error": "No content IDs provided"}), 400
        
        contents = content_service.get_content_by_ids(content_ids)
        
        # Add CORS headers to the response
        resp = jsonify(contents)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error fetching content by IDs: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/popular-tags', methods=['GET', 'OPTIONS'])
def get_popular_tags():
    """Get most popular tags."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        limit = int(request.args.get('limit', 20))
        
        tags = content_service.get_popular_tags(limit)
        
        # Add CORS headers to the response
        resp = jsonify(tags)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error fetching popular tags: {e}")
        return jsonify({"error": str(e)}), 500

@content_bp.route('/recent-content', methods=['GET', 'OPTIONS'])
def get_recent_content():
    """Get recent content with pagination."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        result = content_service.get_recent_content(page, page_size)
        
        # Add CORS headers to the response
        resp = jsonify(result)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error fetching recent content: {e}")
        return jsonify({"error": str(e)}), 500 