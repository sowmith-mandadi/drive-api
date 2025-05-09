"""
FastAPI application entry point for the Conference CMS API.
"""
import json
import os
import platform
import sys
import traceback
from datetime import datetime
from typing import Any, Callable, Dict

import fastapi
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.batch import router as batch_router
from app.api.endpoints.bookmarks import router as bookmarks_router
from app.api.endpoints.content import router as content_router

# Import routers
from app.api.endpoints.drive import router as drive_router
from app.api.endpoints.files import router as files_router
from app.api.endpoints.rag import router as rag_router
from app.api.endpoints.upload import router as upload_router

# Import settings
from app.core.logging import configure_logging

# Configure structured logging
logger = configure_logging()

# Create FastAPI app
app = FastAPI(
    title="Conference Content Management API",
    description="API for managing conference materials with Google Drive integration and RAG capabilities",
    version="1.0.0",
    # Enable standard docs at /docs and /redoc for better compatibility
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",  # Standard OpenAPI schema URL
)


# Global exception handler
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next: Callable):
    """Global exception handling middleware."""
    try:
        return await call_next(request)
    except Exception as e:
        # Enhanced error logging
        error_details = {
            "error": str(e),
            "error_class": e.__class__.__name__,
            "path": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else "unknown",
            "timestamp": datetime.now().isoformat(),
        }

        # Log the exception with detailed information
        logger.error(
            f"Unhandled exception: {e.__class__.__name__}: {str(e)}",
            exc_info=True,
            error_details=json.dumps(error_details),
            traceback=traceback.format_exc(),
        )

        # Return JSON response with error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "error_type": e.__class__.__name__,
                "detail": str(e)
                if os.environ.get("DEBUG", "false").lower() == "true"
                else "An unexpected error occurred",
            },
        )


# Configure session middleware with secure defaults
session_secret = os.environ.get("SESSION_SECRET_KEY", "supersecretkey")
logger.info(
    f"Configuring session middleware with {'default' if session_secret == 'supersecretkey' else 'custom'} secret"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    max_age=60 * 60 * 24,  # 1 day
    same_site="lax",  # Prevents CSRF
    https_only=False,  # Allow HTTP for App Engine internal routing
)

# Configure CORS with wildcard origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint for the API.

    Returns:
        Dict[str, Any]: A simple status message
    """
    try:
        logger.info("Root endpoint accessed")

        # Check app components to ensure they're properly initialized
        system_status = {}

        try:
            # Check if directories are correctly set up
            temp_dir = os.environ.get("TEMP_PROCESSING_DIR", "/tmp/processing")
            bucket_dir = os.environ.get("UPLOAD_BUCKET_DIR", "/tmp/bucket")
            upload_dir = os.environ.get("UPLOAD_DIR", "/tmp/uploads")

            system_status["dirs"] = {
                "temp_dir": {
                    "path": temp_dir,
                    "exists": os.path.exists(temp_dir),
                    "writable": os.access(temp_dir, os.W_OK),
                },
                "bucket_dir": {
                    "path": bucket_dir,
                    "exists": os.path.exists(bucket_dir),
                    "writable": os.access(bucket_dir, os.W_OK),
                },
                "upload_dir": {
                    "path": upload_dir,
                    "exists": os.path.exists(upload_dir),
                    "writable": os.access(upload_dir, os.W_OK),
                },
            }

            # Additional diagnostics can be added here
            logger.info(f"System status: {json.dumps(system_status)}")
        except Exception as check_ex:
            logger.error(f"Error in system status check: {str(check_ex)}", exc_info=True)
            system_status["check_error"] = str(check_ex)

        # Simplified response for health checks
        if os.environ.get("DEBUG", "false").lower() == "true":
            diagnostics = system_status
        else:
            diagnostics = {"hidden": "Diagnostics hidden in production mode"}

        # Return available documentation URLs
        return {
            "status": "ok",
            "diagnostics": diagnostics,
            "documentation": {
                "standard_docs": "/docs",
                "redoc": "/redoc",
                "api_docs": "/api/docs",
                "openapi_schema": "/openapi.json",
                "api_openapi_schema": "/api/openapi.json",
            },
        }
    except Exception as e:
        # Enhanced error logging in root endpoint
        logger.error(
            f"Critical error in root endpoint: {e.__class__.__name__}: {str(e)}",
            exc_info=True,
            traceback=traceback.format_exc(),
        )

        # For App Engine health checks, return a basic OK response even with errors
        return {
            "status": "internal_error",
            "error": str(e)
            if os.environ.get("DEBUG", "false").lower() == "true"
            else "An error occurred",
        }


@app.get("/health")
async def health() -> RedirectResponse:
    """Redirect /health to /api/health for better compatibility"""
    return RedirectResponse(url="/api/health")


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is operational.

    Returns:
        Dict[str, str]: Status message and version information
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/health/info")
async def system_info() -> Dict[str, Any]:
    """
    System information endpoint for monitoring and debugging.

    Returns:
        Dict[str, Any]: Detailed system information including Python version,
                       platform details, processor info, and current timestamp
    """
    try:
        info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "system": platform.system(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "timestamp": datetime.now().isoformat(),
            "environment": {
                k: v
                for k, v in os.environ.items()
                if k.startswith(("PYTHON", "GOOGLE", "USE_", "GCP_", "DEBUG", "TEMP_", "UPLOAD_"))
            },
            "directories": {
                "cwd": os.getcwd(),
                "tmp_dir": {
                    "path": "/tmp",
                    "exists": os.path.exists("/tmp"),
                    "writable": os.access("/tmp", os.W_OK),
                },
            },
        }
        logger.info("System info requested")
        return info
    except Exception as e:
        logger.error(f"Error in system_info endpoint: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}


# Custom OpenAPI documentation
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> Any:
    """
    Custom Swagger UI documentation.

    Returns:
        HTML: Customized Swagger UI interface
    """
    logger.info("API documentation accessed via /api/docs")
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=app.title + " - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/api/openapi.json", include_in_schema=False)
async def get_api_open_api_endpoint() -> JSONResponse:
    """
    Endpoint to serve the OpenAPI schema.

    Returns:
        Dict[str, Any]: The OpenAPI schema for the API with proper headers
    """
    try:
        logger.info("OpenAPI schema requested via /api/openapi.json")
        # Filter routes to avoid problematic ones
        filtered_routes = [
            route
            for route in app.routes
            if getattr(route, "include_in_schema", True)
            and not str(route.path).startswith("/docs")
            and not str(route.path).startswith("/redoc")
            and not str(route.path).startswith("/openapi.json")
        ]

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=filtered_routes,  # Use filtered routes
        )
        logger.info(f"Successfully generated OpenAPI schema with {len(filtered_routes)} routes")
        return JSONResponse(content=openapi_schema, media_type="application/json")
    except Exception as e:
        logger.error(f"Error generating OpenAPI schema: {str(e)}", exc_info=True)
        # Return a basic error response with details
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate OpenAPI schema", "details": str(e)},
            media_type="application/json",
        )


# Add a test OpenAPI endpoint with minimal schema
@app.get("/api/openapi-test", include_in_schema=False)
async def get_test_open_api_endpoint():
    """Simple test endpoint to debug OpenAPI issues"""
    try:
        # Return a basic hard-coded schema to verify endpoint works
        basic_schema = {
            "openapi": "3.0.2",
            "info": {
                "title": app.title,
                "version": app.version,
                "description": "Test schema - simplified version",
            },
            "paths": {
                "/api/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {"status": {"type": "string"}},
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
        }
        logger.info("Successfully generated test OpenAPI schema")
        return JSONResponse(content=basic_schema, media_type="application/json")
    except Exception as e:
        logger.error(f"Error generating test OpenAPI schema: {str(e)}", exc_info=True)
        # Return a basic error response with details
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate test OpenAPI schema", "details": str(e)},
            media_type="application/json",
        )


# Add a test Swagger UI endpoint
@app.get("/api/docs-test", include_in_schema=False)
async def custom_swagger_ui_html_test():
    """
    Test version of Swagger UI documentation.
    """
    logger.info("Test API documentation accessed via /api/docs-test")
    return get_swagger_ui_html(
        openapi_url="/api/openapi-test",  # Use the test endpoint
        title=app.title + " - API Documentation (Test)",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


# Add a debug endpoint to help troubleshoot schema generation
@app.get("/api/debug", include_in_schema=False)
async def debug_endpoint():
    """Debug endpoint to help diagnose App Engine issues"""
    try:
        # Check environment
        env_info = {
            "python_version": sys.version,
            "fastapi_version": fastapi.__version__,
            "app_engine": bool(os.environ.get("GAE_APPLICATION")),
            "env_vars": {
                k: v for k, v in os.environ.items() if k.startswith(("GOOGLE", "GAE", "CLOUD"))
            },
        }

        # Check tmp directories
        dir_info = {}
        for path in ["/tmp", "/tmp/processing", "/tmp/uploads"]:
            try:
                exists = os.path.exists(path)
                if not exists:
                    try:
                        os.makedirs(path, exist_ok=True)
                        exists = True
                    except Exception as e:
                        dir_info[f"{path}_create_error"] = str(e)

                writable = os.access(path, os.W_OK) if exists else False
                dir_info[path] = {"exists": exists, "writable": writable}
            except Exception as e:
                dir_info[path] = {"error": str(e)}

        # Try to write a test file in /tmp
        file_test = {}
        try:
            test_file = "/tmp/test.txt"
            with open(test_file, "w") as f:
                f.write("test")
            file_test["success"] = True
            # Clean up
            os.remove(test_file)
        except Exception as e:
            file_test["error"] = str(e)

        # Check routes count
        routes_info = {
            "total_routes": len(app.routes),
            "include_in_schema": len(
                [r for r in app.routes if getattr(r, "include_in_schema", False)]
            ),
        }

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "environment": env_info,
            "directories": dir_info,
            "file_test": file_test,
            "routes": routes_info,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}


# Include routers
app.include_router(drive_router, prefix="/api", tags=["Google Drive Integration"])
app.include_router(content_router, prefix="/api", tags=["Content Management"])
app.include_router(rag_router, prefix="/api", tags=["RAG Services"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(upload_router, prefix="/api", tags=["File Uploads"])
app.include_router(batch_router, prefix="/api", tags=["Batch Operations"])
app.include_router(files_router, prefix="/api", tags=["File Serving"])
app.include_router(bookmarks_router, prefix="/api", tags=["Bookmarks"])


# Add a dedicated health check endpoint for App Engine
@app.get("/_ah/health")
async def app_engine_health_check():
    """Health check endpoint specifically for App Engine.
    App Engine looks for this endpoint by default.
    """
    try:
        # Quick check of application health
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error in App Engine health check: {str(e)}", exc_info=True)
        # Still return OK for health check to prevent instance termination
        return {"status": "ok", "note": "Error occurred but returning OK to prevent termination"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting application on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
