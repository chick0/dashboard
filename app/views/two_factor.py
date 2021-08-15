
from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp import random_base32
from pyotp import TOTP

from app import db
from app.models import TwoFactor
from app.check import is_two_factor_enabled
from app.check import is_login


bp = Blueprint(
    name="two_factor",
    import_name="two_factor",
    url_prefix="/two-factor"
)


@bp.get("/turn-on")
def on():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 활성화 되어 있다면
    if is_two_factor_enabled():
        # 대시보드로 이동하기
        return redirect(url_for("dashboard.dashboard"))

    # 2단계 인증 시크릿 키 생성하기
    secret = random_base32()

    # 2단계 인증 세션 만들기
    session['tmp_two_factor'] = {
        "secret": secret,
        "work": "on"
    }

    # OTP QR 코드를 위한 URL 생성
    qr_url = TOTP(secret).provisioning_uri(
        name=f"Dashboard 2fa ({session['user']['email']})"
    )

    return render_template(
        "dashboard/two_factor/on.html",
        qr_url=qr_url
    )


@bp.get("/turn-off")
def off():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증이 비활성화 되어 있다면
    if not is_two_factor_enabled():
        # 대시보드로 이동하기
        return redirect(url_for("dashboard.dashboard"))

    # 2단계 인증 시크릿 키 가져오기
    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    # 2단계 인증 세션 만들기
    session['tmp_two_factor'] = {
        "secret": two_factor.secret,
        "work": "off"
    }

    return redirect(url_for("dashboard.two_factor.check"))


@bp.get("/check")
def check():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증 세션이 없다면 대시보드로 이동하기
    if session.get("tmp_two_factor", None) is None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/check")
def check_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증 세션을 세션에서 가져오기
    two_factor = session.get("tmp_two_factor", None)

    # 2단계 인증 세션이 없다면 대시보드로 이동
    if two_factor is None:
        return redirect(url_for("dashboard.dashboard"))

    # 입력받은 OTP 토큰 불러오기
    otp = request.form.get("token", None)

    # 입력받은 토큰이 없다면
    if otp is None:
        # 입력 폼으로 이동하기
        return redirect(url_for("dashboard.two_factor.check"))

    # OTP 토큰 검증하기
    if not TOTP(two_factor['secret']).verify(otp):
        # 일치하지 않는다면 입력 폼으로 이동하기
        return redirect(url_for("dashboard.two_factor.check"))

    # 2단계 인증을 활성화 하는 모드라면
    if two_factor['work'] == "on":
        # 2단계 인증 정보 새로 만들기
        new_two_factor = TwoFactor()
        new_two_factor.user_idx = session['user']['idx']
        new_two_factor.secret = two_factor['secret']

        # 데이터베이스에 만든 2단계 인증 정보 추가하기
        db.session.add(new_two_factor)

        session['two_factor'] = {
            "status": True,
            "passed": False,
        }
    else:
        # 발견한 2단계 인증 정보가 있다면 삭제하기
        TwoFactor.query.filter_by(
            user_idx=session['user']['idx']
        ).delete()

        session['two_factor'] = {
            "status": False,
            "passed": False,
        }

    # 변경사항 데이터베이스에 저장하기
    db.session.commit()

    # 2단계 인증 세션 삭제하기
    del session['tmp_two_factor']
    return redirect(url_for("dashboard.dashboard"))
