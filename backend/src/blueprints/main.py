import time
from sqlalchemy import text
from flask import Blueprint, current_app, jsonify
from src.extensions import db

bp = Blueprint("main", __name__)

@bp.route("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    llm_status = "available" if current_app.config.get("LLM") else "unavailable"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "service": "rainbow6-backend",
        "version": "1.0.0",
        "dependencies": {
            "database": db_status,
            "llm_service": llm_status
        }
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return jsonify(health_data), status_code

@bp.route("/ready")
def readiness_check():
    return jsonify({
        "status": "ready",
        "timestamp": time.time()
    })
