"""
Entry point for the Conference Content Management API.
Run this file to start the application.
"""

import os
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Print out all registered routes
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    # Get port from environment or use default (3001)
    port = int(os.environ.get("PORT", 3001))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True) 