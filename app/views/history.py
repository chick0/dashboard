
from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import History
from app.check import is_login


bp = Blueprint(
    name="history",
    import_name="history",
    url_prefix="/history"
)


@bp.get("")
def show_all():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    history_list = History.query.filter_by(
        email=session['user']['email']
    ).all()

    return render_template(
        "dashboard/history/show_all.html",
        history_list=history_list
    )


@bp.get("/<int:idx>")
def detail(idx: int):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    history = History.query.filter_by(
        idx=idx,
        email=session['user']['email'],
    ).first()
    if history is None:
        return redirect(url_for("dashboard.history.show_all"))

    return render_template(
        "dashboard/history/detail.html",
        history=history
    )


@bp.get("/<int:idx>/delete")
def delete(idx: int):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    History.query.filter_by(
        idx=idx,
        email=session['user']['email'],
    ).delete()

    db.session.commit()

    return redirect(url_for("dashboard.history.show_all"))
