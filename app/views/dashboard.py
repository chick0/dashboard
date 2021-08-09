
from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.check import is_two_factor_enabled
from app.check import is_login
from app.mail import send
from . import login
from . import register
from . import delete
from . import application
from . import two_factor
from . import password
from . import lost


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
bp.register_blueprint(password.bp)
bp.register_blueprint(lost.bp)


@bp.get("/logout")
def logout():
    for key in list(session.keys()):
        del session[key]

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
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    email = request.form.get("email", session['user']['email'])
    nickname = request.form.get("name", session['user']['nickname'])

    user = User.query.filter_by(
        idx=session['user']['idx']
    ).first()

    if nickname != user.nickname:
        session['user'] = {
            "idx": user.idx,
            "email": user.email,
            "nickname": nickname,
        }

        user.nickname = nickname
        db.session.commit()

    if email != user.email:
        token = send(target_address=email)
        session['email_update'] = {
            "email": email,
            "token": token
        }
        return redirect(url_for("dashboard.email_update"))

    return redirect(url_for("dashboard.dashboard"))


@bp.get("/email/update")
def email_update():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    new_email = session.get("email_update", None)
    if new_email is None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/email_update.html",
        email=new_email['email']
    )


@bp.post("/email/update")
def email_update_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    new_email = session.get("email_update", None)
    if new_email is None:
        return redirect(url_for("dashboard.dashboard"))

    token = request.form.get("token", None)
    if token is None or new_email['token'] != token:
        return redirect(url_for("dashboard.email_update"))
    else:
        user = User.query.filter_by(
            idx=session['user']['idx']
        ).first()

        session['user'] = {
            "idx": user.idx,
            "email": new_email['email'],
            "nickname": user.nickname,
        }

        user.email = new_email['email']
        db.session.commit()

    return redirect(url_for("dashboard.dashboard"))
