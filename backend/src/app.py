import os
import json
from flask import Flask
from .extensions import db

def create_app():
    app = Flask(__name__, template_folder="templates")

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rainbow6.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Ladda copy.json
    copy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "copy.json")
    with open(copy_path, "r", encoding="utf-8") as f:
        app.config["COPY"] = json.load(f)

    # Blueprints (⬅️ måste vara inne i create_app, inte utanför)
    from .controllers.main_controller import bp as main_bp
    from .controllers.db_controller import bp as db_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(db_bp)

    # Skapa tabeller
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)