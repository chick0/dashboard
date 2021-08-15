from secrets import token_bytes

from flask import Blueprint
from flask import session
from flask import abort
from flask import redirect
from flask import url_for

from app import db
from app.models import Application
from app.models import ApplicationSecret
from app.check import is_login


bp = Blueprint(
    name="secret",
    import_name="secret",
    url_prefix="/secret"
)


@bp.get("/<int:app_idx>/create")
def create(app_idx: int):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 있는 어플리케이션으로 요청한건지 확인
    # 해당 어플리케이션의 주인이 로그인한 사용자인지 확인
    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return abort(404)

    # 어플리케이션 시크릿 키를 만들었는지 확인
    if ApplicationSecret.query.filter_by(
        target_idx=app.idx
    ).first() is None:
        # 만들지 않았다면 새로 만들기
        secret = ApplicationSecret()
        secret.target_idx = app.idx
        secret.key = token_bytes(32).hex()

        # 데이터베이스에 저장하기
        db.session.add(secret)
        db.session.commit()

        # 시크릿 키를 세션에 저장하기
        # - 1번만 보여주기 위해서
        session['secret:key'] = secret.key

    return redirect(url_for("dashboard.application.detail.show", app_idx=app_idx) + "#secret_key")


@bp.get("/<int:app_idx>/delete")
def delete(app_idx: int):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 있는 어플리케이션으로 요청한건지 확인
    # 해당 어플리케이션의 주인이 로그인한 사용자인지 확인
    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return abort(404)

    # 어플리케이션 시크릿 키를 만들었다면 삭제하기
    ApplicationSecret.query.filter_by(
        target_idx=app.idx
    ).delete()

    # 데이터베이스에 저장하기
    db.session.commit()

    return redirect(url_for("dashboard.application.detail.show", app_idx=app_idx))
