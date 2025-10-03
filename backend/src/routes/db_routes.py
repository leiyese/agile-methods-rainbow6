from flask import Blueprint
from ..controllers.db_controller import db_test

bp = Blueprint("db", __name__)
bp.add_url_rule("/db-test", view_func=db_test, methods=["GET"])