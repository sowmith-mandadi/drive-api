"""
Configuration settings for the FastAPI application.
"""
import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Base settings for the application."""

    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Conference Content Management API"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",  # Angular default
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://localhost",
    ]

    # Frontend Settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:4200")

    # Google API Settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/callback"
    )

    # Google Drive API Scopes
    GOOGLE_DRIVE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
    ]

    # Upload Settings
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 100))

    # RAG Settings
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_PROJECT: Optional[str] = os.getenv("VERTEX_AI_PROJECT")
    VERTEX_MODEL_ID: str = os.getenv("VERTEX_MODEL_ID", "text-bison")
    VERTEX_RAG_MODEL: Optional[str] = os.getenv("VERTEX_RAG_MODEL")
    TEXT_EMBEDDING_MODEL: Optional[str] = os.getenv("TEXT_EMBEDDING_MODEL")

    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GCS_BUCKET_NAME: Optional[str] = os.getenv("GCS_BUCKET_NAME")

    # Firestore Settings
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "conference-cms")
    FIRESTORE_COLLECTION_CONTENT: str = os.getenv("FIRESTORE_COLLECTION_CONTENT", "content")
    FIRESTORE_EMULATOR_HOST: Optional[str] = os.getenv("FIRESTORE_EMULATOR_HOST")

    # Session Settings
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "supersecretkey")

    # Flask Settings (for compatibility)
    FLASK_ENV: Optional[str] = os.getenv("FLASK_ENV")

    class Config:
        """Configuration for BaseSettings."""

        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
