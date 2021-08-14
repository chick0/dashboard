from hashlib import sha512

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from pyotp.totp import TOTP

from app import db
from app.models import User
from app.models import History
from app.models import TwoFactor
from app.ip import get_ip
from app.config import SALT_PASSWORD
from app.check import is_two_factor_enabled
from app.check import is_two_factor_passed
from app.check import is_login


bp = Blueprint(
    name="login",
    import_name="login",
    url_prefix="/login"
)


@bp.get("")
def form():
    # 유저가 로그인 상태라면 (+ 2단계 인증 확인 없이)
    if is_login(no_two_factor=True):
        # 근데 만약 2단계 인증을 통과 하지 못 했다면
        if not is_two_factor_passed():
            # 2단계 인증 화면으로 이동
            return redirect(url_for("dashboard.login.two_factor_verify"))

        # 2단계 인증 통과 했음. 대시보드로 이동
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/form.html"
    )


@bp.post("")
def form_post():
    # 폼에서 입력 받은 값 가져오기
    email = request.form.get("email", "")

    # 만약 이메일 주소에 '@'가 없다면
    if email.find("@") == -1:
        # 로그인 화면으로 이동
        return redirect(url_for("dashboard.login.form"))

    ##################################################
    history = History()
    history.email = email[:128]
    # history.is_failed = ???
    history.ip = get_ip()
    history.user_agent = request.user_agent
    ##################################################

    # 로그인할 유저 정보를 데이터베이스에서 불러오기
    user = User.query.filter_by(
        email=email[:128],
        password=sha512(f"{request.form.get('password', '')}+{SALT_PASSWORD}".encode()).hexdigest(),
    ).first()
    if user is None:
        # 발견된 유저가 없다면, 로그인 기록에 [실패]로 저장하기
        history.is_failed = True
        db.session.add(history)
        db.session.commit()

        return redirect(url_for("dashboard.login.form"))
    else:
        # 로그인 성공! 로그인 기록에 [성공]으로 저장하기
        history.is_failed = False
        db.session.add(history)
        db.session.commit()

    # 2단계 인증이 활성화된 상태인지 확인하고 세션에 저장하기
    two_factor = TwoFactor.query.filter_by(
        user_idx=user.idx
    ).first()
    if two_factor is None:
        session['two_factor'] = {
            "status": False,   # 2단계 인증 비활성화
            "passed": False,   # 2단계 인증을 통과한 상태가 아님
        }
    else:
        session['two_factor'] = {
            "status": True,    # 2단계 인증 활성화
            "passed": False,   # 2단계 인증을 통과한 상태가 아님
        }

    # 세션에 유저 정보 저장하기
    session['user'] = {
        "idx": user.idx,
        "email": user.email,
        "nickname": user.nickname,
    }

    return redirect(url_for("dashboard.dashboard"))


@bp.get("/two-factor")
def two_factor_verify():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login(no_two_factor=True):
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/login/two_factor.html"
    )


@bp.post("/two-factor")
def two_factor_verify_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login(no_two_factor=True):
        return redirect(url_for("dashboard.dashboard"))

    # 2단계 인증이 비활성화 상태라면 대시보드로 이동하기
    if not is_two_factor_enabled():
        return redirect(url_for("dashboard.dashboard"))

    # 폼에서 입력 받은 값 가져오기
    token = request.form.get("token", None)
    if token is None:
        # 없으면 입력 폼으로 돌아가기
        return redirect(url_for("dashboard.login.verify"))

    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    # 입력 받은 토큰과 일치하는지 확인하기
    result = TOTP(two_factor.secret).verify(otp=token)

    # 입력 받은 토큰이 일치함
    if result:
        session['two_factor'] = {
            "status": True,    # 2단계 인증 활성화
            "passed": True,    # 2단계 인증을 통과한 상태임
        }

    return redirect(url_for("dashboard.dashboard"))
