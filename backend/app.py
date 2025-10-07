from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
from api.ask import ask_blueprint
from api.upload import upload_blueprint
from api.analyze import analyze_blueprint
from api.offices import offices_blueprint

# Create Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

# Register blueprints
app.register_blueprint(ask_blueprint, url_prefix='/api')
app.register_blueprint(upload_blueprint, url_prefix='/api')
app.register_blueprint(analyze_blueprint, url_prefix='/api')
app.register_blueprint(offices_blueprint, url_prefix='/api')

# Root route
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/under-construction")
def under_construction():
    return render_template("under_construction.html")

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
