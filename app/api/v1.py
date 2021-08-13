
from flask import Blueprint
from flask import jsonify

from app import db
from app.models import User
from app.models import Application
from app.models import ApplicationSecret
from app.models import Code
from app.models import Token
from app.scope import v1


bp = Blueprint(
    name="v1",
    import_name="v1",
    url_prefix="/v1"
)


@bp.get("/token")
def token():
    # TODO:토큰 생성 코드를 이용해 토큰 생성하고 리턴하기
    # TODO:코드 만료시 400 코드 만료됨 리턴하기

    # TODO:코드 사용후 삭제하기

    return jsonify({
        "status": "todo"
    })


@bp.get("/user")
def user():
    # TODO:토큰 받고 만료되었는지 확인하기
    # TODO:만료된 토큰 사용시 400 토큰 만료됨 리턴하기

    # TODO:스코프에 알맞는 정보만 리턴하기

    return jsonify({
        "status": "todo",
        "user": {
            "id": int,
            "email": str,
            "nickname": str,
        }
    })
