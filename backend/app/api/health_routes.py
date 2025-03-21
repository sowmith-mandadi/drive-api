"""Health check routes for the API."""

from flask import Blueprint, jsonify
import platform
import sys
import os
from datetime import datetime

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@health_bp.route('/info', methods=['GET'])
def system_info():
    """Return system information."""
    return jsonify({
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat()
    }) 