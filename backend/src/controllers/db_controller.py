from flask import Blueprint
from sqlalchemy import text
from ..app import db

bp = Blueprint("db", __name__)

@bp.route("/db-test")
def db_test():
    try:
        # Use text() for raw SQL queries
        db.session.execute(text("SELECT 1"))
        return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}, 500