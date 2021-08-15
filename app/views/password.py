from hashlib import sha512

from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp import TOTP

from app import db
from app.models import User
from app.models import TwoFactor
from app.config import SALT_PASSWORD
from app.check import is_two_factor_enabled
from app.check import is_login


bp = Blueprint(
    name="password",
    import_name="password",
    url_prefix="/password"
)


@bp.get("/step1")
def step1():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    return render_template(
        "dashboard/password/step1.html"
    )


@bp.post("/step1")
def step1_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 입력받은 비밀번호 불러오기
    password = request.form.get("password", None)

    # 입력받은 비밀번호가 없다면
    if password is None:
        # 비밀번호 입력 폼으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 비밀번호 해시 만들기
    password_hash = sha512(f"{password}+{SALT_PASSWORD}".encode()).hexdigest()

    # 로그인중인 유저 정보와 입력 받은 비밀번호를 이용해 유저 검색하기
    user = User.query.filter_by(
        idx=session['user']['idx'],
        email=session['user']['email'],
        password=password_hash
    ).first()

    # 검색된 유저가 없으면
    if user is None:
        # 비밀번호 입력 폼으로 이동
        return redirect(url_for("dashboard.password.step1"))

    # 비밀번호 변경 세션 세션에 저장하기
    session['password_update'] = {
        "raw_password": password,
        "old_password": password_hash,
        "otp_passed": not is_two_factor_enabled()
    }

    # 만약 2단계 인증이 활성화 되어 있다면 2단계 인증으로 넘어가기
    if is_two_factor_enabled():
        return redirect(url_for("dashboard.password.step2"))

    # 아니면 새로운 비밀번호 입력 폼으로 이동하기
    return redirect(url_for("dashboard.password.step3"))


@bp.get("/step2")
def step2():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 비밀번호 변경 세션을 세션에서 가져오기
    password_update = session.get("password_update", None)

    # 비밀번호 변경 세션이 없다면
    if password_update is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 만약 2단계 인증이 활성화 되어있지 않다면 다음 단계로 이동하기
    if not is_two_factor_enabled():
        return redirect(url_for("dashboard.password.step3"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/step2")
def step2_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 비밀번호 변경 세션을 세션에서 가져오기
    password_update = session.get("password_update", None)

    # 비밀번호 변경 세션이 없다면
    if password_update is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 유저 아이디로 2단계 인증 시크릿 키 데이터베이스에서 가져오기
    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    # 발견된 시크릿 키가 없다면
    if two_factor is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 검색한 시크릿 키로 OTP 인증하기
    if TOTP(two_factor.secret).verify(request.form.get("token", "")):
        # 만약 서버에서 생성한 코드가 입력 받은 코드와 일치한다면
        # 비밀번호 변경 세션에 OTP 통과 상태로 업데이트 하기
        session['password_update'] = {
            "raw_password": password_update['raw_password'],
            "old_password": password_update['old_password'],
            "otp_passed": True
        }

        # 다음 단계로 이동하기
        return redirect(url_for("dashboard.password.step3"))
    else:
        # 아니라면, 입력 폼으로 돌아가기
        return redirect(url_for("dashboard.password.step2"))


@bp.get("/step3")
def step3():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 비밀번호 변경 세션을 세션에서 가져오기
    password_update = session.get("password_update", None)

    # 비밀번호 변경 세션이 없다면
    if password_update is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    return render_template(
        "dashboard/password/step3.html"
    )


@bp.post("/step3")
def step3_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 비밀번호 변경 세션을 세션에서 가져오기
    password_update = session.get("password_update", None)

    # 비밀번호 변경 세션이 없다면
    if password_update is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 로그인중인 유저 데이터와 1단계에서 입력 받은 비밀번호를 이용해 데이터베이스에서 유저정보를 검색하기
    user = User.query.filter_by(
        email=session['user']['email'],
        password=password_update['old_password']
    ).first()

    # 일치하는 유저가 없다면
    if user is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.password.step1"))

    # 만약 2단계 인증을 통과한 상태라면
    if password_update['otp_passed']:
        # 입력받은 비밀번호로 유저 비밀번호 업데이트 하기
        user.password = sha512(
            f"{request.form.get('password', password_update['raw_password'])}+{SALT_PASSWORD}".encode()
        ).hexdigest()

        # 변경사항 데이터베이스에 저장하기
        db.session.commit()
    else:
        # 2단계 인증화면으로 이동하기
        return redirect(url_for("dashboard.password.step2"))

    # 사용된 비밀번호 변경 세션 삭제하기
    del session['password_update']
    return redirect(url_for("dashboard.dashboard"))
