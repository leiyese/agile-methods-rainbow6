from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
from backend.api.ask import ask_blueprint
from backend.api.upload import upload_blueprint
from backend.api.analyze import analyze_blueprint
from backend.api.rag_api import rag_blueprint  # RAG-API för vektorsökning

# Create Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

# Register blueprints
app.register_blueprint(ask_blueprint, url_prefix='/api')
app.register_blueprint(upload_blueprint, url_prefix='/api')
app.register_blueprint(analyze_blueprint, url_prefix='/api')
app.register_blueprint(rag_blueprint)  # RAG-API för vektorsökning

# Root route
@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "message": "RAG API is running",
        "endpoints": [
            "/api/rag/search",
            "/api/rag/hybrid-search",
            "/api/rag/ask",
            "/api/rag/add"
        ]
    })

@app.route("/under-construction")
def under_construction():
    return jsonify({
        "status": "under_construction",
        "message": "This endpoint is under construction"
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
