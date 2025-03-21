"""RAG (Retrieval-Augmented Generation) routes for the API."""

from flask import Blueprint, request, jsonify
import logging
from app.services.rag_service import RagService

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

# Initialize services
rag_service = RagService()

@rag_bp.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    """Ask a question using RAG."""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
        
    try:
        data = request.json
        question = data.get('question', '')
        content_ids = data.get('contentIds', None)
        filters = data.get('filters', None)
        
        logger.info(f"RAG question received: {question}")
        
        response = rag_service.get_rag_response(
            question=question,
            content_ids=content_ids,
            filters=filters
        )
        
        # Add CORS headers to the response
        resp = jsonify(response)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    except Exception as e:
        logger.error(f"Error in RAG question answering: {e}")
        return jsonify({"error": f"Error processing question: {str(e)}"}), 500

@rag_bp.route('/summarize', methods=['POST'])
def summarize_document():
    """Summarize a document using Vertex AI."""
    try:
        data = request.json
        content_id = data.get('contentId', '')
        
        logger.info(f"Summarize request for content ID: {content_id}")
        
        summary = rag_service.summarize_document(content_id)
        
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        logger.error(f"Error in document summarization: {e}")
        return jsonify({"error": f"Error summarizing document: {str(e)}"}), 500

@rag_bp.route('/generate-tags', methods=['POST'])
def generate_tags():
    """Generate tags for a document using Vertex AI."""
    try:
        data = request.json
        content_id = data.get('contentId', '')
        
        logger.info(f"Generate tags request for content ID: {content_id}")
        
        tags = rag_service.generate_tags(content_id)
        
        return jsonify(tags)
    except Exception as e:
        logger.error(f"Error in tag generation: {e}")
        return jsonify({"error": f"Error generating tags: {str(e)}"}), 500

@rag_bp.route('/similar', methods=['POST'])
def find_similar():
    """Find similar documents based on a query or content ID."""
    try:
        data = request.json
        query = data.get('query')
        content_id = data.get('contentId')
        limit = data.get('limit', 5)
        
        logger.info(f"Find similar documents request: {data}")
        
        similar_docs = rag_service.find_similar_documents(
            query=query,
            content_id=content_id,
            limit=limit
        )
        
        return jsonify(similar_docs)
    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        return jsonify({"error": f"Error finding similar documents: {str(e)}"}), 500 