from flask import Blueprint, current_app, render_template

bp = Blueprint("main", __name__)

@bp.route("/", endpoint="index")
def index():
    copy = current_app.config.get("COPY", {})
    return render_template("index.html", copy=copy)

@bp.route("/under-construction", endpoint="under_construction")
def under_construction():
    return render_template("under_construction.html")