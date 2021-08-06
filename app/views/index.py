
from flask import Blueprint
from flask import render_template


bp = Blueprint(
    name="index",
    import_name="index",
    url_prefix="/"
)


@bp.get("/")
def about():
    return render_template(
        "index/about.html"
    )
