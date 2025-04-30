"""
Configuration settings for the FastAPI application.
"""
import os
from typing import List, Optional, Union

from pydantic import BaseModel, validator

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Settings(BaseModel):
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
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))

    # RAG Settings
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_PROJECT: Optional[str] = os.getenv("VERTEX_AI_PROJECT")
    VERTEX_MODEL_ID: str = os.getenv("VERTEX_MODEL_ID", "text-bison")
    VERTEX_RAG_MODEL: Optional[str] = os.getenv("VERTEX_RAG_MODEL")
    TEXT_EMBEDDING_MODEL: Optional[str] = os.getenv("TEXT_EMBEDDING_MODEL")

    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GCS_BUCKET_NAME: Optional[str] = os.getenv("GCS_BUCKET_NAME")

    # Google Cloud Storage Settings
    USE_GCS: bool = os.getenv("USE_GCS", "false").lower() == "true"
    GCS_FOLDER_PREFIX: str = os.getenv("GCS_FOLDER_PREFIX", "uploads")
    GCS_MAKE_PUBLIC: bool = os.getenv("GCS_MAKE_PUBLIC", "false").lower() == "true"
    GCS_URL_EXPIRATION: int = int(os.getenv("GCS_URL_EXPIRATION", "3600"))  # 1 hour in seconds

    # Cloud Tasks Settings
    USE_CLOUD_TASKS: bool = os.getenv("USE_CLOUD_TASKS", "false").lower() == "true"
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    VECTOR_PROCESSING_QUEUE: str = os.getenv("VECTOR_PROCESSING_QUEUE", "vector-processing")
    VECTOR_PROCESSING_ENDPOINT: str = os.getenv("VECTOR_PROCESSING_ENDPOINT", "")
    TASK_DISPATCH_DEADLINE: int = int(os.getenv("TASK_DISPATCH_DEADLINE", "600"))  # 10 minutes
    TASK_SCHEDULE_DELAY: int = int(os.getenv("TASK_SCHEDULE_DELAY", "0"))  # 0 = immediate execution

    # Firestore Settings
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "conference-cms")
    FIRESTORE_COLLECTION_CONTENT: str = os.getenv("FIRESTORE_COLLECTION_CONTENT", "content")
    FIRESTORE_EMULATOR_HOST: Optional[str] = os.getenv("FIRESTORE_EMULATOR_HOST")

    # Session Settings
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "supersecretkey")

    # Flask Settings (for compatibility)
    FLASK_ENV: Optional[str] = os.getenv("FLASK_ENV")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        raise ValueError(v)


# Create settings instance
settings = Settings()
