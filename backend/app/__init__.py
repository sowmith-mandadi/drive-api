"""Application factory module for the Flask app."""

from flask import Flask
from flask_cors import CORS
import os
import logging

# Import blueprints
from app.api.content_routes import content_bp
from app.api.rag_routes import rag_bp
from app.api.health_routes import health_bp
from app.api.drive_routes import drive_bp

def create_app(config_object=None):
    """Create and configure the Flask application.
    
    Args:
        config_object: Configuration object to use.
        
    Returns:
        Flask application instance.
    """
    # Create the Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        # Default to using environment variable for config
        from config.settings import get_config
        app.config.from_object(get_config())
    
    # Set maximum upload file size (100 MB by default)
    max_upload_size = int(os.environ.get('MAX_UPLOAD_SIZE_MB', 100)) * 1024 * 1024
    app.config['MAX_CONTENT_LENGTH'] = max_upload_size
    
    # Configure request timeout for file uploads (5 minutes by default)
    app.config['FLASK_MAX_BODY_SIZE'] = max_upload_size
    app.config['REQUEST_TIMEOUT'] = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', 300))
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting the Conference Content Management API")
    logger.info(f"Maximum upload size: {max_upload_size / (1024 * 1024):.1f} MB")
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "X-Requested-With", "Accept", "Authorization", "Origin"])
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.error(f"File too large: {error}")
        return {"error": f"File too large. Maximum size is {max_upload_size / (1024 * 1024):.1f} MB"}, 413
    
    # Register blueprints with /api prefix
    app.register_blueprint(content_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(drive_bp)
    
    # Create a simple root route
    @app.route('/')
    def index():
        return {"message": "Conference Content Management API is running"}
    
    return app 