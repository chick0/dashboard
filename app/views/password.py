from hashlib import sha512

from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp import TOTP

from app import db
from app.models import User
from app.models import TwoFactor
from app.config import SALT_PASSWORD
from app.check import is_two_factor_enabled
from app.check import is_login


bp = Blueprint(
    name="password",
    import_name="password",
    url_prefix="/password"
)


@bp.get("/step1")
def step1():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    return render_template(
        "dashboard/password/step1.html"
    )


@bp.post("/step1")
def step1_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    password = request.form.get("password", None)
    if password is None:
        return redirect(url_for("dashboard.password.step1"))

    password_hash = sha512(f"{password}+{SALT_PASSWORD}".encode()).hexdigest()

    user = User.query.filter_by(
        idx=session['user']['idx'],
        email=session['user']['email'],
        password=password_hash
    ).first()
    if user is None:
        return redirect(url_for("dashboard.password.step1"))

    session['password_update'] = {
        "raw_password": password,
        "old_password": password_hash,
        "otp_passed": not is_two_factor_enabled()
    }

    if is_two_factor_enabled():
        return redirect(url_for("dashboard.password.step2"))

    return redirect(url_for("dashboard.password.step3"))


@bp.get("/step2")
def step2():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    password_update = session.get("password_update", None)
    if password_update is None:
        return redirect(url_for("dashboard.password.step1"))

    if not is_two_factor_enabled():
        return redirect(url_for("dashboard.password.step3"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/step2")
def step2_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    password_update = session.get("password_update", None)
    if password_update is None:
        return redirect(url_for("dashboard.password.step1"))

    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()
    if two_factor is None:
        return redirect(url_for("dashboard.password.step1"))

    if TOTP(two_factor.secret).verify(request.form.get("token", "")):
        session['password_update'] = {
            "raw_password": password_update['raw_password'],
            "old_password": password_update['old_password'],
            "otp_passed": True
        }

        return redirect(url_for("dashboard.password.step3"))
    else:
        return redirect(url_for("dashboard.password.step2"))


@bp.get("/step3")
def step3():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    password_update = session.get("password_update", None)
    if password_update is None:
        return redirect(url_for("dashboard.password.step1"))

    return render_template(
        "dashboard/password/step3.html"
    )


@bp.post("/step3")
def step3_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    password_update = session.get("password_update", None)
    if password_update is None:
        return redirect(url_for("dashboard.password.step1"))

    user = User.query.filter_by(
        email=session['user']['email'],
        password=password_update['old_password']
    ).first()
    if user is None:
        return redirect(url_for("dashboard.password.step1"))

    if password_update['otp_passed']:
        user.password = sha512(
            f"{request.form.get('password', password_update['raw_password'])}+{SALT_PASSWORD}".encode()
        ).hexdigest()
        db.session.commit()
    else:
        return redirect(url_for("dashboard.password.step2"))

    del session['password_update']
    return redirect(url_for("dashboard.dashboard"))
