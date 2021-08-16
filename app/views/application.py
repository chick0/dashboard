
from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Application
from app.models import Token
from app.check import is_two_factor_enabled
from app.check import is_login
from app.check import url_verifier
from app.custom_error import TwoFactorRequired
from . import detail
from . import secret


bp = Blueprint(
    name="application",
    import_name="application",
    url_prefix="/application"
)
bp.register_blueprint(detail.bp)
bp.register_blueprint(secret.bp)


@bp.get("")
def show_all():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    app_list = []

    # 유저가 로그인한 어플리케이션의 토큰 목록 불러오기
    for this in Token.query.filter_by(
        target_idx=session['user']['idx']
    ).all():
        # 토큰에 저장된 어플리케이션 아이디로 어플리케이션 데이터베이스에서 불러오기
        app = Application.query.filter_by(
            idx=this.application_idx,
            delete=False
        ).first()

        # 삭제된 어플리케이션이 아니라면
        if app is not None:
            # 목록에 추가하기
            app_list.append(app)
        else:
            # 해당 토큰 삭제하기
            db.session.delete(this)

            # 변경사항 데이터베이스에 저장하기
            db.session.commit()

    return render_template(
        "dashboard/application/app_list.html",
        app_list=app_list,
        _title=f"{session['user']['nickname']}님이 로그인한 어플리케이션"
    )


@bp.get("/my")
def my():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 로그인한 유저가 주인인 어플리케이션 검색하기
    app_list = Application.query.filter_by(
        owner_idx=session['user']['idx'],
        delete=False
    ).all()

    return render_template(
        "dashboard/application/app_list.html",
        app_list=app_list,
        _title=f"{session['user']['nickname']}님이 만든 어플리케이션"
    )


@bp.get("/register")
def register():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 상태라면
    if not is_two_factor_enabled():
        # 2단계 인증이 필요하다는 오류 리턴하기
        raise TwoFactorRequired

    return render_template(
        "dashboard/application/register.html"
    )


@bp.post("/register")
def register_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 상태라면
    if not is_two_factor_enabled():
        # 2단계 인증이 필요하다는 오류 리턴하기
        raise TwoFactorRequired

    # 유저한테 입력받은 정보로 어플리케이션 생성하기
    app = Application()
    app.name = request.form.get("name", "이름 없는 어플리케이션")[:20]
    app.owner_idx = session['user']['idx']

    # 유저한테 입력받은 홈페이지 주소가 올바른지 검증하기
    app.homepage = url_verifier(
        url=request.form.get("homepage", "http://localhost:8082"),
        fallback="http://localhost:8082"
    )[:32]

    # 유저한테 입력받은 콜백 링크가 올바른지 검증하기
    app.callback = url_verifier(
        url=request.form.get("callback", "http://localhost:8082/login/callback"),
        fallback="http://localhost:8082/login/callback"
    )[:500]

    # 앱은 삭제된 상태가 아님
    app.delete = False

    # 데이터베이스에 생성한 어플리케이션 정보 저장하기
    db.session.add(app)
    db.session.commit()

    return redirect(url_for("dashboard.application.detail.show", app_idx=app.idx))
