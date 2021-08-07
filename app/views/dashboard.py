
from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from . import login
from . import register


bp = Blueprint(
    name="dashboard",
    import_name="dashboard",
    url_prefix="/dashboard"
)
bp.register_blueprint(login.bp)
bp.register_blueprint(register.bp)


@bp.get("")
def dashboard():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    return render_template(
        "dashboard/dashboard.html"
    )


@bp.post("")
def user_update():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    return redirect(url_for("dashboard.dashboard"))
