from uuid import uuid4
from time import time
from secrets import token_bytes

from flask import Blueprint
from flask import abort
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Application
from app.models import Code
from app.models import Token
from app.check import is_login
from app.custom_error import OAuthTimeOut


bp = Blueprint(
    name="oauth",
    import_name="oauth",
    url_prefix="/oauth"
)


@bp.get("")
def ask():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    try:
        # 어플리케이션 아이디 불러오기
        app_id = int(request.args.get("app_id", "None"))

        # 아이디 값은 0보다 크므로 0보다 작거나 같은 아이디 값은 잘못된 값
        if app_id <= 0:
            return abort(400)
    except ValueError:
        # 어플리케이션 아이디를 전달 받지 못한 경우
        return abort(400)

    # 전달받은 어플리케이션 아이디를 통해 어플리케이션 검색하기
    app = Application.query.filter_by(
        idx=app_id,
        delete=False
    ).first()

    # 검색된 어플리케이션이 없다면 오류 리턴하기
    if app is None:
        return abort(404)

    # 권한 범위 불러오기, 기본 값은 유저 아이디 읽기 권한
    scope = request.args.get("scope", "id")

    # OAuth 정보를 저장할 아이디 만들기
    key = uuid4().__str__()

    # 세션에 OAuth 세션 정보 저장하기
    session[f"oauth:{key}"] = {
        "app_id": app.idx,                  # 어플리케이션 아이읻
        "scope": scope,                     # 권한 범위
        "user_id": session['user']['idx'],  # 유저 아이디
        "time": int(time())                 # 요청 시간 (타임 아웃 체크용)
    }

    return render_template(
        "oauth/ask.html",
        app=app,
        scope=scope,
        key=key
    )


@bp.get("/<string:key>")
def callback(key: str):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 세션에 저장된 OAuth 세션 정보 불러오기
    oauth_data = session.get(f"oauth:{key}", None)

    # 저장된 값이 없다면 오류 리턴하기
    if oauth_data is None:
        return abort(400)

    # 5분 타임 아웃 체크하기
    if int(time()) - oauth_data['time'] >= 300:
        raise OAuthTimeOut

    # 어플리케이션 아이디를 이용해서 데이터베이스에서 검색하기
    app = Application.query.filter_by(
        idx=oauth_data['app_id'],
        delete=False
    ).first()

    # 발견된 어플리케이션이 없다면 오류 리턴하기
    if app is None:
        return abort(404)

    # API 요청을 위한 토큰 생성 코드 생성하기
    code = Code()
    code.application_idx = app.idx
    code.target_idx = oauth_data['user_id']
    code.scope = oauth_data['scope']
    code.code = token_bytes(16).hex()

    # 데이터베이스에 저장하기
    db.session.add(code)
    db.session.commit()

    # 사용된 OAuth 세션 정보 삭제하기
    del session[f"oauth:{key}"]

    # 등록된 콜백 링크로 토큰 생성 코드와 함께 이동하기
    return redirect(app.callback + f"?code={code.code}")


@bp.get("/revoke/<string:app_idx>")
def revoke(app_idx: str):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 기존에 생성한 토큰이 있다면 삭제하기
    Token.query.filter_by(
        application_idx=app_idx,
        target_idx=session['user']['idx']
    ).delete()

    # 변견사항 데이터베이스에 저장하기
    db.session.commit()

    return redirect(url_for("dashboard.application.show_all"))
