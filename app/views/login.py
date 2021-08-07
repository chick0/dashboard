from hashlib import sha512

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp.totp import TOTP

from app import db
from app.models import User
from app.models import History
from app.ip import get_ip


bp = Blueprint(
    name="login",
    import_name="login",
    url_prefix="/login"
)


@bp.get("")
def form():
    login_user = session.get("user", None)
    if login_user is not None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/form.html"
    )


@bp.post("")
def form_post():
    email = request.form.get("email", "")
    at = email.find("@")
    if at == -1:
        return redirect(url_for("dashboard.login.form"))

    ##################################################
    history = History()
    history.email = email
    history.is_failed = False
    history.ip = get_ip()
    history.user_agent = request.user_agent
    ##################################################

    user = User.query.filter_by(
        email=email,
        password=sha512(request.form.get("password", "").encode()).hexdigest(),
    ).first()
    if user is None:
        history.is_failed = True
        db.session.add(history)
        db.session.commit()

        return redirect(url_for("dashboard.login.form"))

    db.session.add(history)
    db.session.commit()

    session['user'] = {
        "idx": user.idx,
        "email": user.email,
        "nickname": user.nickname,
    }

    return redirect(url_for("dashboard.dashboard"))


@bp.get("/2fa")
def verify():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    return render_template(
        "dashboard/login/2fa.html"
    )


@bp.get("/2fa")
def verify_post():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    token = request.form.get("token", None)
    if token is None:
        return redirect(url_for("dashboard.login.verify"))

    # TODO:디비 모델 만들기
    # TODO:OTP 인증 만들기

    # TOTP("secret").verify(otp=token)

    return redirect(url_for("dashboard.dashboard"))
