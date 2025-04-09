"""
FastAPI application entry point for the Conference CMS API.
"""
import os
import platform
import sys
from datetime import datetime
from typing import Dict, Any, List

import structlog
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn
from starlette.middleware.sessions import SessionMiddleware

# Import routers
from app.api.endpoints.drive import router as drive_router
from app.api.endpoints.content import router as content_router
from app.api.endpoints.rag import router as rag_router
from app.api.endpoints.auth import router as auth_router

# Import settings
from app.core.config import settings
from app.core.logging import configure_logging

# Configure structured logging
logger = configure_logging()

# Create FastAPI app
app = FastAPI(
    title="Conference Content Management API",
    description="API for managing conference materials with Google Drive integration and RAG capabilities",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Configure session middleware
# In production, use a more secure secret key
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.environ.get("SESSION_SECRET_KEY", "supersecretkey"),
    max_age=60 * 60 * 24  # 1 day
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint for the API.
    
    Returns:
        Dict[str, str]: A simple status message
    """
    logger.info("Root endpoint accessed")
    return {"message": "Conference Content Management API is running"}

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is operational.
    
    Returns:
        Dict[str, str]: Status message and version information
    """
    logger.info("Health check endpoint accessed")
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/api/health/info")
async def system_info() -> Dict[str, Any]:
    """
    System information endpoint for monitoring and debugging.
    
    Returns:
        Dict[str, Any]: Detailed system information including Python version,
                       platform details, processor info, and current timestamp
    """
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat()
    }
    logger.info("System info requested", **info)
    return info

# Custom OpenAPI documentation
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> Any:
    """
    Custom Swagger UI documentation.
    
    Returns:
        HTML: Customized Swagger UI interface
    """
    logger.info("API documentation accessed")
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=app.title + " - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/api/openapi.json", include_in_schema=False)
async def get_open_api_endpoint() -> Dict[str, Any]:
    """
    Endpoint to serve the OpenAPI schema.
    
    Returns:
        Dict[str, Any]: The OpenAPI schema for the API
    """
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Include routers
app.include_router(drive_router, prefix="/api", tags=["Google Drive Integration"])
app.include_router(content_router, prefix="/api", tags=["Content Management"])
app.include_router(rag_router, prefix="/api", tags=["RAG Services"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting application on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 