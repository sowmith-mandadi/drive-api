"""
WSGI entry point for the Conference Content Management API.
Used for production deployment with Gunicorn.
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Directly run with Flask's development server if executed
    app.run() 