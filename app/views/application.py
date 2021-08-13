
from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Application
from app.models import Token
from app.check import is_two_factor_enabled
from app.check import is_login
from app.check import url_verifier
from app.custom_error import TwoFactorRequired
from . import detail


bp = Blueprint(
    name="application",
    import_name="application",
    url_prefix="/application"
)
bp.register_blueprint(detail.bp)


@bp.get("")
def show_all():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    app_list = []
    for this in Token.query.filter_by(
        target_idx=session['user']['idx']
    ).all():
        app = Application.query.filter_by(
            idx=this.application_idx,
            delete=False
        ).first()

        if app is not None:
            app_list.append(app)

    return render_template(
        "dashboard/application/app_list.html",
        app_list=app_list,
        _title=f"{session['user']['nickname']}님이 로그인한 어플리케이션"
    )


@bp.get("/my")
def my():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    app_list = Application.query.filter_by(
        owner_idx=session['user']['idx'],
        delete=False
    ).all()

    return render_template(
        "dashboard/application/app_list.html",
        app_list=app_list,
        _title=f"{session['user']['nickname']}님이 만든 어플리케이션"
    )


@bp.get("/register")
def register():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        raise TwoFactorRequired

    return render_template(
        "dashboard/application/register.html"
    )


@bp.post("/register")
def register_post():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        raise TwoFactorRequired

    app = Application()
    app.name = request.form.get("name", "이름 없는 어플리케이션")[:20]
    app.owner_idx = session['user']['idx']
    app.homepage = url_verifier(
        url=request.form.get("homepage", "http://localhost:8082")[:32],
        fallback="http://localhost:8082"
    )
    app.callback = url_verifier(
        url=request.form.get("homepage", "http://localhost:8082/login/callback")[:32],
        fallback="http://localhost:8082/login/callback"
    )
    app.delete = False

    db.session.add(app)
    db.session.commit()

    return redirect(url_for("dashboard.application.detail.show", app_idx=app.idx))
