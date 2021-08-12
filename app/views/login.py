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
from app.models import TwoFactor
from app.ip import get_ip
from app.config import SALT_PASSWORD
from app.check import is_two_factor_enabled
from app.check import is_two_factor_passed
from app.check import is_login


bp = Blueprint(
    name="login",
    import_name="login",
    url_prefix="/login"
)


@bp.get("")
def form():
    if is_login(no_two_factor=True):
        if not is_two_factor_passed():
            return redirect(url_for("dashboard.login.two_factor_verify"))

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
    history.email = email[:128]
    # history.is_failed = ???
    history.ip = get_ip()
    history.user_agent = request.user_agent
    ##################################################

    user = User.query.filter_by(
        email=email[:128],
        password=sha512(f"{request.form.get('password', '')}+{SALT_PASSWORD}".encode()).hexdigest(),
    ).first()
    if user is None:
        history.is_failed = True
        db.session.add(history)
        db.session.commit()

        return redirect(url_for("dashboard.login.form"))
    else:
        history.is_failed = False
        db.session.add(history)
        db.session.commit()

    two_factor = TwoFactor.query.filter_by(
        user_idx=user.idx
    ).first()
    if two_factor is None:
        session['two_factor'] = {
            "status": False,
            "passed": False,
        }
    else:
        session['two_factor'] = {
            "status": True,
            "passed": False,
        }

    session['user'] = {
        "idx": user.idx,
        "email": user.email,
        "nickname": user.nickname,
    }

    return redirect(url_for("dashboard.dashboard"))


@bp.get("/two-factor")
def two_factor_verify():
    if not is_login(no_two_factor=True):
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/two-factor")
def two_factor_verify_post():
    if not is_login(no_two_factor=True):
        return redirect(url_for("dashboard.dashboard"))

    if not is_two_factor_enabled():
        return redirect(url_for("dashboard.dashboard"))

    token = request.form.get("token", None)
    if token is None:
        return redirect(url_for("dashboard.login.verify"))

    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    result = TOTP(two_factor.secret).verify(otp=token)

    if result:
        session['two_factor'] = {
            "status": True,
            "passed": True,
        }

    return redirect(url_for("dashboard.dashboard"))
