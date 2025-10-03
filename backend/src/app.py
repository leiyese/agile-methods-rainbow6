import os
import sys

# Add the directory containing this script to sys.path
# This allows for absolute imports relative to the 'src' directory
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import json
from flask import Flask
from .extensions import db, cors


def create_app():
    app = Flask(__name__, template_folder="templates")

    raw_url = os.environ.get("DATABASE_URL")
    if raw_url and raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_url or "sqlite:///rainbow6.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    })

    db.init_app(app)

    is_prod = os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER") == "true"
    if is_prod:
        frontend_url = os.environ.get("FRONTEND_URL")
        if frontend_url:
            cors.init_app(app, origins=[frontend_url])
        else:
            cors.init_app(app, origins=[])
    else:
        cors.init_app(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    try:
        copy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "copy.json")
        with open(copy_path, "r", encoding="utf-8") as f:
            app.config["COPY"] = json.load(f)
    except FileNotFoundError:
        app.config["COPY"] = {}
    except json.JSONDecodeError:
        app.config["COPY"] = {}


    from .controllers.main_controller import bp as main_bp
    from .controllers.db_controller import bp as db_bp
    from .routes.assistant_routes import bp as assistant_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(assistant_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
