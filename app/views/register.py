from time import time
from hashlib import sha512

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.mail import send
from app import db
from app.models import User
from app.config import SALT_PASSWORD


bp = Blueprint(
    name="register",
    import_name="register",
    url_prefix="/register"
)


@bp.get("")
def form():
    return redirect(url_for("dashboard.register.step1"))


@bp.get("/step1")
def step1():
    login_user = session.get("user", None)
    if login_user is not None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/register/step1.html"
    )


@bp.post("/step1")
def step1_post():
    email = request.form.get("email", None)
    if email is None:
        return redirect(url_for("dashboard.register.step1"))

    at = email.find("@")
    if at == -1:
        return redirect(url_for("dashboard.register.step1"))

    check_using = User.query.filter_by(
        email=email
    ).first()
    if check_using is not None:
        return render_template(
            "dashboard/register/using_email.html"
        ), 400

    token = send(target_address=email)
    session['register'] = {
        "email": email,
        "token": token,
        "checked": False,
        "date": int(time()),
    }

    return redirect(url_for("dashboard.register.step2"))


@bp.get("/step2")
def step2():
    register = session.get("register", None)
    if register is None:
        return redirect(url_for("dashboard.register.step1"))

    return render_template(
        "dashboard/register/step2.html",
        email=register['email'],
        token=register['token'],
    )


@bp.post("/step2")
def step2_post():
    register = session.get("register", None)
    if register is None:
        return redirect(url_for("dashboard.register.step1"))

    if int(time()) - register['date'] > 600:
        session['register'] = None
        del session['register']
        return redirect(url_for("dashboard.register.step1"))

    token = request.form.get("token")
    if register['token'] == token:
        register['checked'] = True
        session['register'] = register

        return redirect(url_for("dashboard.register.step3"))

    return redirect(url_for("dashboard.register.step2"))


@bp.get("/step3")
def step3():
    register = session.get("register", None)
    if register is None:
        return redirect(url_for("dashboard.register.step1"))

    return render_template(
        "dashboard/register/step3.html",
        nickname=register['email'].split("@")[0]
    )


@bp.post("/step3")
def step3_post():
    register = session.get("register", None)
    if register is None:
        return redirect(url_for("dashboard.register.step1"))

    nickname = request.form.get("nickname", register['email'].split("@")[0])
    password = request.form.get("password", None)
    if password is None:
        return redirect(url_for("dashboard.register.step3"))

    user = User()
    user.email = register['email']
    user.password = sha512(f"{password}+{SALT_PASSWORD}".encode()).hexdigest()
    user.nickname = nickname[:32]
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("dashboard.login.form"))
