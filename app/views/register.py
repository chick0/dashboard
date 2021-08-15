from time import time
from hashlib import sha512

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.mail import send
from app.check import is_login
from app import db
from app.models import User
from app.config import SALT_PASSWORD


bp = Blueprint(
    name="register",
    import_name="register",
    url_prefix="/register"
)


@bp.get("")
def form():
    return redirect(url_for("dashboard.register.step1"))


@bp.get("/step1")
def step1():
    # 로그인 상태라면 대시보드로 이동하기
    if is_login():
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "dashboard/register/step1.html"
    )


@bp.post("/step1")
def step1_post():
    # 폼에서 입력 받은 값 가져오기
    email = request.form.get("email", "")

    # 만약 이메일 주소에 '@'가 없다면
    if email.find("@") == -1:
        # 로그인 화면으로 이동
        return redirect(url_for("dashboard.register.step1"))

    # 회원가입을 시도하는 이메일 주소를 사용하고 있는 계정을 데이터베이스에서 검색하기
    check_using = User.query.filter_by(
        email=email
    ).first()

    # 계정이 발견되었다면 사용할 수 없는 이메일이라고 안내하는 페이지 리턴
    if check_using is not None:
        return render_template(
            "dashboard/register/using_email.html"
        ), 400

    # 인증을 위한 인증토큰 전송
    token = send(target_address=email)

    # 회원가입 세션 생성
    session['register'] = {
        "email": email,
        "token": token,
        "checked": False,
        "date": int(time()),
    }

    return redirect(url_for("dashboard.register.step2"))


@bp.get("/step2")
def step2():
    # 회원가입 세션을 세션에서 가져오기
    register = session.get("register", None)

    # 회원가입 세션이 없다면
    if register is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.register.step1"))

    return render_template(
        "dashboard/register/step2.html",
        email=register['email'],
        token=register['token'],
    )


@bp.post("/step2")
def step2_post():
    # 회원가입 세션을 세션에서 가져오기
    register = session.get("register", None)

    # 회원가입 세션이 없다면
    if register is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.register.step1"))

    # 시간초과 확인하기
    if int(time()) - register['date'] > 600:
        # 회원가입 세션 초기화하기
        del session['register']

        # 맨처음 화면으로 이동
        return redirect(url_for("dashboard.register.step1"))

    # 입력받은 토큰 값 불러오기
    token = request.form.get("token", "")

    # 회원가입 세션에 있는 토큰과 입력받은 토큰이 일치하다면
    if register['token'] == token:
        # 회원가입 세션에있는 이메일 인증 통과 처리하기
        register['checked'] = True

        # 세션에 저장된 회원가입 세션 업데이트 하기
        session['register'] = register

        # 다음 단계로 넘어가기
        return redirect(url_for("dashboard.register.step3"))

    # 다시 입력 폼으로 돌아가기
    return redirect(url_for("dashboard.register.step2"))


@bp.get("/step3")
def step3():
    # 회원가입 세션을 세션에서 가져오기
    register = session.get("register", None)

    # 회원가입 세션이 없다면
    if register is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.register.step1"))

    return render_template(
        "dashboard/register/step3.html",
        nickname=register['email'].split("@")[0]
    )


@bp.post("/step3")
def step3_post():
    # 회원가입 세션을 세션에서 가져오기
    register = session.get("register", None)

    # 회원가입 세션이 없다면
    if register is None:
        # 맨처음 화면으로 이동하기
        return redirect(url_for("dashboard.register.step1"))

    # 입력받은 닉네임 값 가져오기
    nickname = request.form.get("nickname", register['email'].split("@")[0])

    # 입력받은 비밀번호 값 가져오기
    password = request.form.get("password", None)

    # 입력받은 비밀번호가 없거나 비밀번호가 8자리 보다 짧다면
    if password is None or len(password) < 8:
        # 입력 폼으로 돌아가기
        return redirect(url_for("dashboard.register.step3"))

    # 유저 생성
    user = User()
    user.email = register['email'][:128]
    user.password = sha512(f"{password}+{SALT_PASSWORD}".encode()).hexdigest()
    user.nickname = nickname[:32]

    # 데이터베이스에 유저 추가하고 변경사항 저장하기
    db.session.add(user)
    db.session.commit()

    # 회원가입 세션 삭제하기
    del session['register']
    return redirect(url_for("dashboard.login.form"))
