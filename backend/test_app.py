from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route("/")
def index():
    return jsonify({"message": "Conference Content Management API is running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Starting minimal Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)