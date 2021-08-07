
from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.check import is_two_factor_enabled
from app.check import is_login
from . import login
from . import register
from . import delete
from . import application
from . import two_factor


bp = Blueprint(
    name="dashboard",
    import_name="dashboard",
    url_prefix="/dashboard"
)
bp.register_blueprint(login.bp)
bp.register_blueprint(register.bp)
bp.register_blueprint(delete.bp)
bp.register_blueprint(application.bp)
bp.register_blueprint(two_factor.bp)


@bp.get("/logout")
def logout():
    try:
        del session['user']
        del session['two_factor']

    except KeyError:
        pass

    return redirect(url_for("dashboard.login.form"))


@bp.get("")
def dashboard():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    return render_template(
        "dashboard/dashboard.html",
        two_factor=is_two_factor_enabled()
    )


@bp.post("")
def user_update():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    return redirect(url_for("dashboard.dashboard"))
