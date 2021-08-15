from datetime import datetime
from datetime import timedelta
from secrets import token_bytes

from flask import Blueprint
from flask import request
from flask import current_app
from flask import jsonify
from jwt import encode
from jwt import decode

from app import db
from app.models import User
from app.models import Application
from app.models import ApplicationSecret
from app.models import Code
from app.models import Token
from app.custom_error import ApiErrorCodeExpired
from app.custom_error import ApiErrorTokenExpired
from app.custom_error import ApiAuthFail
from app.custom_error import ApiApplicationSecretInvalid
from app.custom_error import ApiErrorAppNotFound
from app.custom_error import ApiErrorUserNotFound


bp = Blueprint(
    name="v1",
    import_name="v1",
    url_prefix="/v1"
)


@bp.get("/token")
def token():
    # 토큰 생성 코드 불러오기
    code = request.args.get("code", "#")
    if len(code) != 32:
        return jsonify({
            "error": "token generation code length is 32"
        }), 400

    # 어플리케이션 시크릿키 불러오기
    secret = request.args.get("secret", "#")
    if len(secret) != 64:
        return jsonify({
            "error": "application secret key length is 64"
        }), 400

    # 데이터베이스에서 토큰 생성 코드 검색하기
    code = Code.query.filter_by(
        code=code
    ).first()

    # 없는 코드라면 오류 리턴하기
    if code is None:
        raise ApiAuthFail

    # 토큰 생성 코드가 만료 되었는지 확인하기
    if code.date + timedelta(minutes=10) <= datetime.now():
        # 시간 초과 오류 리턴하기
        raise ApiErrorCodeExpired

    # 어플리케이션 시크릿 검색하기
    app_sec = ApplicationSecret.query.filter_by(
        target_idx=code.application_idx,
        key=secret
    ).first()

    # 일치하는 것이 데이터베이스에 없다면 오류 리턴하기
    if app_sec is None:
        raise ApiApplicationSecretInvalid

    # 기존에 생성된 토큰 검색하고 있다면 삭제하기
    Token.query.filter_by(
        application_idx=code.application_idx,
        target_idx=code.target_idx
    ).delete()

    # 새로운 토큰 생성하기
    new_token = Token()
    new_token.application_idx = code.application_idx
    new_token.target_idx = code.target_idx
    new_token.scope = code.scope
    new_token.token = token_bytes(64).hex()

    # 변경사항 데이터베이스에 저장하기
    db.session.add(new_token)
    db.session.delete(code)
    db.session.commit()

    return jsonify({
        "token": encode(
            payload={
                "idx": new_token.idx,
                "app": new_token.application_idx
            },
            key=current_app.config['SECRET_KEY'].hex(),
            algorithm="HS256"
        ),
        "scope": new_token.scope
    }), 201


@bp.get("/user")
def user():
    # 인증 토큰이 담긴 헤더 읽기
    auth = request.headers.get("authorization", default=None)

    # 토큰 정보가 없으면 오류 리턴하기
    if auth is None:
        raise ApiAuthFail

    try:
        must_be_bearer, jwt = auth.split(" ")

        # 토큰의 종류가 Bearer 가 아니라면 오류 리턴하기
        if must_be_bearer != "Bearer":
            raise TypeError
    except ValueError:
        return jsonify({
            "error": "authorization token syntax error",
            "more-information": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization"
        }), 400
    except TypeError:
        return jsonify({
            "error": "token type is not 'Bearer'",
        }), 400

    # JWT 토큰 디코딩 하기
    payload = decode(jwt, key=current_app.config['SECRET_KEY'].hex(), algorithms=["HS256"])

    try:
        # 페이로드에서 토큰 아이디와 앱 아이디 불러오기
        # 올바르지 않은 값이 있으면 오류 리턴하기
        token_id = int(payload.get("idx", 0))
        app_id = int(payload.get("app", 0))
    except ValueError:
        raise ApiAuthFail

    # 아이디는 1부터 시작하므로 0보다 작거나 같은 아이디는 올바르지 않은 값
    if token_id <= 0 or app_id <= 0:
        raise ApiAuthFail

    # 토큰 아이디와 앱 아이디를 통해 토큰 정보를 데이터베이스에서 검색하기
    token_from_db = Token.query.filter_by(
        idx=token_id,
        application_idx=app_id
    ).first()

    # 검색결과가 없으면 오류 리턴하기
    if token_from_db is None:
        raise ApiAuthFail

    # 토큰이 만료 되었는지 확인하기
    if token_from_db.date + timedelta(hours=6) <= datetime.now():
        # 시간 초과 오류 리턴하기
        raise ApiErrorTokenExpired

    # 토큰 정보에서 가져온 어플리케이션 아이디를 통해 어플리케이션 정보 검색하기
    app_from_db = Application.query.filter_by(
        idx=token_from_db.application_idx,
        delete=False
    ).first()

    # 발견된 어플리케이션이 없다면 오류 리턴하기
    if app_from_db is None:
        raise ApiErrorAppNotFound

    # 토큰 정보에서 가져온 사용자 아이디를 통해 사용자 정보 검색하기
    user_from_db = User.query.filter_by(
        idx=token_from_db.target_idx
    ).first()

    # 발견된 사용자 정보가 없다면 오류 리턴하기
    if user_from_db is None:
        raise ApiErrorUserNotFound

    # API 결과를 담을 변수 선언하기
    payload = {}

    # 스코프를 구분자를 기준으로 해서 나눔
    scope = token_from_db.scope.split("-")

    # 유저 아이디 읽기 권한이 있다면
    if "id" in scope:
        # API 결과에 유저 아이디 저장하기
        payload['id'] = token_from_db.target_idx

    # 이메일 주소 읽기 권한이 있다면
    if "email" in scope:
        # API 결과에 이메일 주소 저장하기
        payload['email'] = user_from_db.email

    # 닉네임 읽기 권한이 있다면
    if "nickname" in scope:
        # API 결과에 닉네임 저장하기
        payload['nickname'] = user_from_db.nickname

    return jsonify(payload)
