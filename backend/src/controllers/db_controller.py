from flask import Blueprint
from sqlalchemy import text
from ..extensions import db

bp = Blueprint("db", __name__)

@bp.get("/db-test")
def db_test():
    db.session.execute(text("SELECT 1"))
    return {"status": "Database connected successfully!"}