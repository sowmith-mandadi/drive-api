"""
Entry point for the Conference Content Management API.
Run this file to start the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment or use default (3000)
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    print(f"Starting Flask server on port {port} with debug={debug}...")
    app.run(host='0.0.0.0', port=port, debug=debug) 