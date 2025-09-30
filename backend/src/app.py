from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json

# Create db instance
db = SQLAlchemy()

#app
app = Flask(__name__, template_folder="templates")

#database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rainbow6.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Database test route
@app.route("/db-test")
def db_test():
    try:
        # Use text() for raw SQL queries
        db.session.execute(text("SELECT 1"))
        return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}, 500

with open("copy.json") as f:
    copy = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", copy=copy)

@app.route("/under-construction")
def under_construction():
    return render_template("under_construction.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)