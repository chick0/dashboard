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
    code = request.args.get("code", "#")
    if len(code) != 32:
        return jsonify({
            "error": "token generation code length is 32"
        }), 400

    secret = request.args.get("secret", "#")
    if len(secret) != 64:
        return jsonify({
            "error": "application secret key length is 64"
        }), 400

    code = Code.query.filter_by(
        code=code
    ).first()
    if code is None:
        raise ApiAuthFail

    app_sec = ApplicationSecret.query.filter_by(
        target_idx=code.application_idx,
        key=secret
    ).first()
    if app_sec is None:
        raise ApiApplicationSecretInvalid

    ttl = timedelta(minutes=10)
    if code.date + ttl <= datetime.now():
        raise ApiErrorCodeExpired

    Token.query.filter_by(
        application_idx=code.application_idx,
        target_idx=code.target_idx
    ).delete()

    new_token = Token()
    new_token.application_idx = code.application_idx
    new_token.target_idx = code.target_idx
    new_token.scope = code.scope
    new_token.token = token_bytes(64).hex()

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
    auth = request.headers.get("authorization", default=None)
    if auth is None:
        raise ApiAuthFail

    try:
        must_be_bearer, jwt = auth.split(" ")
        if must_be_bearer != "Bearer":
            raise ValueError
    except ValueError:
        return jsonify({
            "error": "authorization token syntax error",
            "more-information": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization"
        }), 400

    payload = decode(jwt, key=current_app.config['SECRET_KEY'].hex(), algorithms=["HS256"])

    try:
        token_id = int(payload.get("idx", 0))
        app_id = int(payload.get("app", 0))
    except ValueError:
        raise ApiAuthFail

    if token_id <= 0:
        raise ApiAuthFail

    token_from_db = Token.query.filter_by(
        idx=token_id,
        application_idx=app_id
    ).first()
    if token_from_db is None:
        raise ApiAuthFail

    ttl = timedelta(hours=6)
    if token_from_db.date + ttl <= datetime.now():
        raise ApiErrorTokenExpired

    app_from_db = Application.query.filter_by(
        idx=token_from_db.application_idx,
        delete=False
    ).first()
    if app_from_db is None:
        raise ApiErrorAppNotFound

    user_from_db = User.query.filter_by(
        idx=token_from_db.target_idx
    ).first()
    if user_from_db is None:
        raise ApiErrorUserNotFound

    payload = {}

    scope = token_from_db.scope.split("-")
    if "id" in scope:
        payload['id'] = token_from_db.target_idx

    if "email" in scope:
        payload['email'] = user_from_db.email

    if "nickname" in scope:
        payload['nickname'] = user_from_db.nickname

    return jsonify(payload)
