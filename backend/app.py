import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Simple Flask app suitable for a React/Node.js frontend
# Endpoints are namespaced under /api to avoid clashing with any static routes

def create_app():
    app = Flask(__name__)

    # Environment-based CORS configuration
    # For Render deployment, get frontend URL from environment variable
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    cors_origins = [frontend_url, 'http://localhost:3000', 'http://localhost:3001']
    
    # Enable CORS for specific origins
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # In-memory store for demo purposes (not persistent)
    items_store = []

    @app.route("/api/health", methods=["GET"]) 
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/items", methods=["GET", "POST"]) 
    def items():
        if request.method == "GET":
            return jsonify({"items": items_store})

        # POST
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "'name' is required"}), 400
        item = {"id": len(items_store) + 1, "name": name}
        items_store.append(item)
        return jsonify(item), 201

    return app


# For Render deployment, create app instance at module level
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
