
from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.models import Token
from app.models import Application
from app.models import ApplicationSecret
from app.check import is_two_factor_enabled
from app.check import is_login
from app.check import url_verifier
from app.custom_error import TwoFactorRequired


bp = Blueprint(
    name="detail",
    import_name="detail",
    url_prefix="/detail"
)


@bp.get("/<string:app_idx>")
def show(app_idx: str):
    # 조회해야하는 어플리케이션 검색하기
    app = Application.query.filter_by(
        idx=app_idx,
        delete=False
    ).first()

    # 검색결과가 없다면
    if app is None:
        # 내가 로그인한 어플리케이션 페이지로 이동하기
        return redirect(url_for("dashboard.application.show_all"))

    # 어플리케이션의 주인 정보 불러오기
    owner = User.query.filter_by(
        idx=app.owner_idx
    ).first()

    # 만약 정보를 조회하고 있는 유저가 로그인한 상태라면
    if is_login():
        # 유저가 이 어플리케이션에 로그인했는지 확인하기
        token = Token.query.filter_by(
            application_idx=app.idx,
            target_idx=session['user']['idx']
        ).first()
    else:
        token = None

    # 어플리케이션의 주인 아이디와 로그인한 유저의 아이디가 일치한가?
    is_owner = app.owner_idx == session.get("user", {}).get("idx", None)

    # 만약 로그인한 유저가 이 어플리케이션의 주인이라면
    if is_owner:
        # 어플리케이션 시크릿을 데이터베이스에서 가져옴
        secret = ApplicationSecret.query.filter_by(
            target_idx=app.idx
        ).first()

        # 방금 시크릿 키를 만들고 이 페이지로 왔다면 세션에 저장된 시크릿 키 값 가져오기
        key = session.get("secret:key", None)

        # 가져온 값이 있다면
        if key is not None:
            # 세션에 저장된 시크릿 키 값 삭제하기
            del session['secret:key']
    else:
        secret = None
        key = None

    return render_template(
        "dashboard/application/detail/show.html",
        app=app,
        token=token,
        owner=owner,
        is_owner=is_owner,
        secret=secret,
        key=key
    )


@bp.get("/<string:app_idx>/edit")
def edit(app_idx: str):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 상태라면
    if not is_two_factor_enabled():
        # 2단계 인증이 필요하다는 오류 리턴하기
        raise TwoFactorRequired

    # 수정 해야하는 어플리케이션의 아이디를 가지고 주인이 로그인한 유저인 어플리케이션 검색하기
    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()

    # 검색결과가 없다면
    if app is None:
        # 내가 만든 어플리케이션 페이지로 이동하기
        return redirect(url_for("dashboard.application.my"))

    return render_template(
        "dashboard/application/detail/edit.html",
        app=app
    )


@bp.post("/<string:app_idx>/edit")
def edit_post(app_idx: str):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 상태라면
    if not is_two_factor_enabled():
        # 2단계 인증이 필요하다는 오류 리턴하기
        raise TwoFactorRequired

    # 수정 해야하는 어플리케이션의 아이디를 가지고 주인이 로그인한 유저인 어플리케이션 검색하기
    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()
    if app is None:
        return redirect(url_for("dashboard.application.my"))

    # 유저한테 입력받은 이름으로 어플리케이션의 이름 수정하기
    app.name = request.form.get("name", app.name)[:20]

    # 유저한테 입력받은 홈페이지 주소가 올바른지 검증하기
    app.homepage = url_verifier(
        url=request.form.get("homepage", "http://localhost:8082"),
        fallback=app.homepage
    )[:32]

    # 유저한테 입력받은 콜백 링크가 올바른지 검증하기
    app.callback = url_verifier(
        url=request.form.get("homepage", "http://localhost:8082/login/callback"),
        fallback=app.callback
    )[:500]

    # 변경사항 저장하기
    db.session.commit()

    return redirect(url_for("dashboard.application.detail.show", app_idx=app.idx))


@bp.get("/<string:app_idx>/delete")
def delete(app_idx: str):
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 상태라면
    if not is_two_factor_enabled():
        # 2단계 인증이 필요하다는 오류 리턴하기
        raise TwoFactorRequired

    # 삭제 해야하는 어플리케이션의 아이디를 가지고 주인이 로그인한 유저인 어플리케이션 검색하기
    app = Application.query.filter_by(
        idx=app_idx,
        owner_idx=session['user']['idx'],
        delete=False
    ).first()

    # 검색결과가 없다면
    if app is None:
        # 내가 만든 어플리케이션 페이지로 이동하기
        return redirect(url_for("dashboard.application.my"))

    # 어플리케이션은 삭제된 상태임
    app.delete = True

    # 이 어플리케이션의 시크릿 키 삭제하기
    ApplicationSecret.query.filter_by(
        target_idx=app_idx
    ).delete()

    # 변경사항 데이터베이스에 저장하기
    db.session.commit()

    return redirect(url_for("dashboard.application.my"))
