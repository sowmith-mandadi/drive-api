"""
Entry point for the Conference Content Management API.
Run this file to start the application.
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
    # Get port from environment or use default (3000)
    port = int(os.environ.get("PORT", 3000))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True) 