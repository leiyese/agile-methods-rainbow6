import os
import sys

script_dir = os.path.dirname(__file__)
project_base_dir = os.path.dirname(script_dir)
if project_base_dir not in sys.path:
    sys.path.insert(0, project_base_dir)

import json
from flask import Flask
from src.extensions import db, cors
from src.blueprints.main import bp as main_bp
from src.blueprints.assistant import bp as assistant_bp

# import llm wrapper
from agents.llm_wrapper import GeminiLLM

from database.init_schema import init_database_schema  
from database.init_documents import init_documents


def create_app():
    app = Flask(__name__, template_folder="templates")

    app.config["LLM"] = GeminiLLM()

    raw_url = os.environ.get("DATABASE_URL")
    if raw_url and raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_url or "sqlite:///rainbow6.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        },
    )

    db.init_app(app)

    is_prod = (
        os.environ.get("FLASK_ENV") == "production"
        or os.environ.get("RENDER") == "true"
    )
    if is_prod:
        frontend_url = os.environ.get("FRONTEND_URL")
        if frontend_url:
            cors.init_app(app, origins=[frontend_url])
        else:
            import warnings
            warnings.warn("FRONTEND_URL not set! CORS will allow only localhost for debugging.")
            raise RuntimeError("FRONTEND_URL must be set in production!")

    else:
        cors.init_app(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    try:
        copy_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "copy.json"
        )
        with open(copy_path, "r", encoding="utf-8") as f:
            app.config["COPY"] = json.load(f)
    except FileNotFoundError:
        app.config["COPY"] = {}
    except json.JSONDecodeError:
        app.config["COPY"] = {}

    app.register_blueprint(main_bp)
    app.register_blueprint(assistant_bp)

    with app.app_context():
        db.create_all()
        
        init_database_schema(db, project_base_dir)
        #init_documents(db, project_base_dir)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)