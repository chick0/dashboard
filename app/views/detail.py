
from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.models import Token
from app.models import Application
from app.check import is_two_factor_enabled
from app.check import is_login
from app.check import url_verifier
from app.custom_error import TwoFactorRequired


bp = Blueprint(
    name="detail",
    import_name="detail",
    url_prefix="/detail"
)


@bp.get("/<string:app_idx>")
def show(app_idx: str):
    app = Application.query.filter_by(
        idx=app_idx,
        delete=False
    ).first()
    if app is None:
        return redirect(url_for("dashboard.application.show_all"))

    owner = User.query.filter_by(
        idx=app.owner_idx
    ).first()

    if is_login():
        token = Token.query.filter_by(
            application_idx=app.idx,
            target_idx=session['user']['idx']
        ).first()
    else:
        token = None

    return render_template(
        "dashboard/application/detail/show.html",
        app=app,
        token=token,
        owner=owner,
        is_owner=app.owner_idx == session.get("user", {}).get("idx", None)
    )


@bp.get("/<string:app_idx>/edit")
def edit(app_idx: str):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        raise TwoFactorRequired

    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return redirect(url_for("dashboard.application.my"))

    return render_template(
        "dashboard/application/detail/edit.html",
        app=app
    )


@bp.post("/<string:app_idx>/edit")
def edit_post(app_idx: str):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        raise TwoFactorRequired

    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return redirect(url_for("dashboard.application.my"))

    app.name = request.form.get("name", app.name)[:20]
    app.homepage = url_verifier(
        url=request.form.get("homepage", app.homepage)[:32],
        fallback=app.homepage
    )
    app.callback = url_verifier(
        url=request.form.get("homepage", app.callback)[:32],
        fallback=app.callback
    )
    db.session.commit()

    return redirect(url_for("dashboard.application.detail.show", app_idx=app.idx))


@bp.get("/<string:app_idx>/delete")
def delete(app_idx: str):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    if not is_two_factor_enabled():
        raise TwoFactorRequired

    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return redirect(url_for("dashboard.application.my"))

    app.delete = True
    db.session.commit()

    return redirect(url_for("dashboard.application.my"))
