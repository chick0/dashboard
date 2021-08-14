
from flask import Blueprint
from flask import redirect
from flask import url_for


bp = Blueprint(
    name="index",
    import_name="index",
    url_prefix="/"
)


@bp.get("")
def goto_dashboard():
    return redirect(url_for("dashboard.dashboard"))
