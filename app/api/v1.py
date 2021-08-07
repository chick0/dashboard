
from flask import Blueprint
from flask import jsonify


bp = Blueprint(
    name="v1",
    import_name="v1",
    url_prefix="/v1"
)

# TODO:유저 토큰 권한에 알맞는 유저 정보 리턴하기
# TODO:OTP 코드 받아서 검증하는 API


@bp.get("")
def hello():
    return jsonify({
        "message": "Hello, World!"
    })
