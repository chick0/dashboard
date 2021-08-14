
from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.models import TwoFactor
from app.check import is_two_factor_enabled
from app.check import is_login
from app.mail import send
from . import login
from . import register
from . import delete
from . import application
from . import two_factor
from . import password
from . import lost
from . import history


bp = Blueprint(
    name="dashboard",
    import_name="dashboard",
    url_prefix="/dashboard"
)
bp.register_blueprint(login.bp)
bp.register_blueprint(register.bp)
bp.register_blueprint(delete.bp)
bp.register_blueprint(application.bp)
bp.register_blueprint(two_factor.bp)
bp.register_blueprint(password.bp)
bp.register_blueprint(lost.bp)
bp.register_blueprint(history.bp)


@bp.get("/logout")
def logout():
    # 세션에 저장된 모든 값 삭제하기
    for key in list(session.keys()):
        del session[key]

    # 로그인 화면으로 이동하기
    return redirect(url_for("dashboard.login.form"))


@bp.get("")
def dashboard():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 2단계 인증 확인하기
    if TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first() is not None:
        # 2단계 인증이 설정되어 있다면,
        # - 2단계 인증 활성화 상태로 세션에 저장하기

        session['two_factor'] = {
            "status": True,
            "passed": session['two_factor']['passed'],
        }

    return render_template(
        "dashboard/dashboard.html",
        two_factor=is_two_factor_enabled()
    )


@bp.post("")
def user_update():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 폼에서 입력 받은 값 가져오기
    email = request.form.get("email", session['user']['email'])
    nickname = request.form.get("name", session['user']['nickname'])

    # 데이터베이스에서 유저 정보 불러오기
    user = User.query.filter_by(
        idx=session['user']['idx']
    ).first()

    # 닉네임이 변경되었다면
    if nickname != user.nickname:
        # 세션에 저장된 유저 정보 업데이트
        session['user'] = {
            "idx": user.idx,
            "email": user.email,
            "nickname": nickname,
        }

        # 디비에 저장된 유저 정보 업데이트
        user.nickname = nickname
        db.session.commit()

    # 이메일이 변경되었다면
    if email != user.email:
        # 해당 이메일 주소로 인증 토큰 발송하기
        token = send(target_address=email)
        session['email_update'] = {
            "email": email,
            "token": token
        }
        return redirect(url_for("dashboard.email_update"))

    return redirect(url_for("dashboard.dashboard"))


@bp.get("/email/update")
def email_update():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 새롭게 변결할 이메일 정보를 세션에서 불러오기
    new_email = session.get("email_update", None)

    # 없다면, 대시보드로 이동
    if new_email is None:
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/email_update.html",
        email=new_email['email']
    )


@bp.post("/email/update")
def email_update_post():
    # 로그인 상태가 아니라면 로그인 화면으로 이동하기
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    # 새롭게 변결할 이메일 정보를 세션에서 불러오기
    new_email = session.get("email_update", None)

    # 없다면, 대시보드로 이동
    if new_email is None:
        return redirect(url_for("dashboard.dashboard"))

    # 폼에서 인증 토큰 불러오기
    token = request.form.get("token", None)

    # 전달 받은 인증 토큰이 없거나 인증 토큰이 일치하지 않는다면
    if token is None or new_email['token'] != token:
        # 입력 폼으로 가서 다시 입력 받기
        return redirect(url_for("dashboard.email_update"))
    else:
        # 데이터베이스에서 유저 정보 불러오기
        user = User.query.filter_by(
            idx=session['user']['idx']
        ).first()

        # 세션에 저장된 유저 정보 업데이트
        session['user'] = {
            "idx": user.idx,
            "email": new_email['email'],
            "nickname": user.nickname,
        }

        # 디비에 저장된 유저 정보 업데이트
        user.email = new_email['email']
        db.session.commit()

    # 대시보드로 이동
    return redirect(url_for("dashboard.dashboard"))
