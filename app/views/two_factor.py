
from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp import random_base32
from pyotp import TOTP

from app import db
from app.models import TwoFactor
from app.check import is_two_factor_enabled
from app.check import is_login


bp = Blueprint(
    name="two_factor",
    import_name="two_factor",
    url_prefix="/two-factor"
)


@bp.get("/turn-on")
def on():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if is_two_factor_enabled():
        return redirect(url_for("dashboard.dashboard"))

    session['two_factor:secret'] = random_base32()
    session['two_factor:work'] = "on"

    qr_url = TOTP(session['two_factor:secret']).provisioning_uri(
        name=f"Dashboard 2fa ({session['user']['email']})"
    )

    return render_template(
        "dashboard/two_factor/on.html",
        qr_url=qr_url
    )


@bp.get("/turn-off")
def off():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        return redirect(url_for("dashboard.dashboard"))

    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    session['two_factor:secret'] = two_factor.secret
    session['two_factor:work'] = "off"

    return redirect(url_for("dashboard.two_factor.check"))


@bp.get("/check")
def check():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if session.get("two_factor:work", None) is None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/check")
def check_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    try:
        is_turn_on = True if session['two_factor:work'] == "on" else False
        secret = session['two_factor:secret']
    except KeyError:
        return redirect(url_for("dashboard.dashboard"))

    otp = request.form.get("token", None)
    if otp is None:
        return redirect(url_for("dashboard.two_factor.check"))

    result = TOTP(secret).verify(otp)

    if result:
        if is_turn_on:
            two_factor = TwoFactor()
            two_factor.user_idx = session['user']['idx']
            two_factor.secret = secret
            db.session.add(two_factor)

            session['two_factor'] = {
                "status": True,
                "passed": False,
            }
        else:
            two_factor = TwoFactor.query.filter_by(
                user_idx=session['user']['idx'],
                secret=secret
            ).first()
            db.session.delete(two_factor)

            session['two_factor'] = {
                "status": False,
                "passed": False,
            }

        db.session.commit()
    else:
        return redirect(url_for("dashboard.two_factor.check"))

    return redirect(url_for("dashboard.dashboard"))
