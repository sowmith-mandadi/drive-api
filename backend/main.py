"""
FastAPI application entry point for the Conference CMS API.
"""
import os
import platform
import sys
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from starlette.middleware.sessions import SessionMiddleware

# Import routers
from app.api.endpoints.drive import router as drive_router
from app.api.endpoints.content import router as content_router
from app.api.endpoints.rag import router as rag_router
from app.api.endpoints.auth import router as auth_router

# Import settings
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Conference Content Management API",
    description="API for managing conference materials with Google Drive integration and RAG capabilities",
    version="1.0.0"
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
async def root():
    """Root endpoint."""
    return {"message": "Conference Content Management API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/api/health/info")
async def system_info():
    """System information endpoint."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat()
    }

# Include routers
app.include_router(drive_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 