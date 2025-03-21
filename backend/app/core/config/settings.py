"""Application settings that load from environment variables."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # Flask application settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google Cloud Platform settings
    GCP_PROJECT_ID = os.getenv('VERTEX_AI_PROJECT_ID', '')
    GCP_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    # Google Cloud Storage settings
    GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'conference-content-bucket')
    
    # Vertex AI settings
    VERTEX_RAG_MODEL = os.getenv('VERTEX_RAG_MODEL', 'gemini-1.5-pro')
    TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL', 'textembedding-gecko@latest')
    
    # Vector Search settings
    VECTOR_INDEX_ENDPOINT = os.getenv('VECTOR_INDEX_ENDPOINT', '')
    VECTOR_INDEX_ID = os.getenv('VECTOR_INDEX_ID', '')
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    # Use test databases and services

# Map environment names to config objects
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Get config based on environment or default to development
def get_config():
    """Return the appropriate configuration object based on the environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig) 