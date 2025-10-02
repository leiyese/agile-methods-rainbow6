from flask import Blueprint
from ..controllers.main_controller import show_index, show_under_construction

bp = Blueprint("main", __name__)
bp.add_url_rule("/", view_func=show_index, endpoint="index", methods=["GET"])
bp.add_url_rule("/under-construction", view_func=show_under_construction,
                endpoint="under_construction", methods=["GET"])