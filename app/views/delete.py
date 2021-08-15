
from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.models import Application
from app.check import is_login


bp = Blueprint(
    name="delete",
    import_name="delete",
    url_prefix="/delete"
)


@bp.get("/ask")
def ask():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 만약 탈퇴하려는 유저가 생성한 어플리케이션이 있다면 탈퇴 실패
    if Application.query.filter_by(
        owner_idx=session['user']['idx'],
        delete=False
    ).first() is not None:
        return render_template(
            "dashboard/delete/failed.html"
        )

    return render_template(
        "dashboard/delete/ask.html"
    )


@bp.post("/ask")
def ask_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 만약 탈퇴하려는 유저가 생성한 어플리케이션이 있다면 탈퇴 실패
    if Application.query.filter_by(
        owner_idx=session['user']['idx'],
        delete=False
    ).first() is not None:
        return render_template(
            "dashboard/delete/failed.html"
        )

    # 로그인한 유저의 계정 삭제하기
    User.query.filter_by(
        idx=session['user']['idx']
    ).delete()

    # 변경사항 저장하기
    db.session.commit()

    # 세션에 저장된 모든 값 삭제하기
    for key in list(session.keys()):
        del session[key]

    # 로그인 화면으로 이동하기
    return redirect(url_for("dashboard.login.form"))
