
from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template


bp = Blueprint(
    name="oauth",
    import_name="oauth",
    url_prefix="/oauth"
)


@bp.get("")
def ask():
    login_user = session.get("user", None)
    if login_user is None:
        return redirect(url_for("dashboard.login.form"))

    app_id = request.args.get("app_id", None)
    scope = request.args.get("scope", None)

    # TODO:유저가 로그인한 상태가 아니라면 dashboard.login 으로 이동
    # TODO:앱이 요구하는 스코프(권한) 유저한테 허용하냐고 물어봄

    return render_template(
        "oauth/ask.html"
    )


@bp.post("")
def callback():
    app_id = request.form.get("app_id", None)
    scope = request.form.get("scope", None)

    # TODO:토큰 생성 코드 생성하기
    # TODO:등록된 앱의 콜백 URL으로 리다이렉트

    callback_url = "/"
    return redirect(callback_url)
