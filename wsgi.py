"""
WSGI entry point for the Conference Content Management API.
This file is used for production deployment with Gunicorn.
"""

import os
import sys

# Add the current directory to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Add the backend directory to the path since that's where the app module is
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backend'))

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # This block only executes when running this file directly, not via Gunicorn
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)), debug=False) 