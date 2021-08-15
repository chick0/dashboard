
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
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 로그인중인 유저와 동일한 이메일로 시도한 기록을 데이터베이스에서 검색하기
    history_list = History.query.filter_by(
        email=session['user']['email']
    ).all()

    return render_template(
        "dashboard/history/show_all.html",
        history_list=history_list
    )


@bp.get("/<int:idx>")
def detail(idx: int):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 기록 아이디와 로그인중인 유저와 동일한 이메일로 시도한 기록을 데이터베이스에서 검색하기
    history = History.query.filter_by(
        idx=idx,
        email=session['user']['email'],
    ).first()

    # 검색결과가 없다면 목록으로 이동하기
    if history is None:
        return redirect(url_for("dashboard.history.show_all"))

    return render_template(
        "dashboard/history/detail.html",
        history=history
    )


@bp.get("/<int:idx>/delete")
def delete(idx: int):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 로그인중인 유저와 동일한 이메일로 시도한 기록을 데이터베이스에서 검색하고 삭제하기
    History.query.filter_by(
        idx=idx,
        email=session['user']['email'],
    ).delete()

    # 변경사항 데이터베이스에 저장하기
    db.session.commit()

    return redirect(url_for("dashboard.history.show_all"))
