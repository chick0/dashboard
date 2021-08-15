from time import time
from time import sleep
from hashlib import sha512

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.mail import send
from app.config import SALT_PASSWORD


bp = Blueprint(
    name="lost",
    import_name="lost",
    url_prefix="/lost"
)


@bp.get("/step1")
def step1():
    # 비밀번호 초기화 단계가 1단계가 맞는지 확인
    step = session.get("lost:step", None)
    if step is not None:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    return render_template(
        "dashboard/lost/step1.html"
    )


@bp.post("/step1")
def step1_post():
    # 비밀번호 초기화 단계가 1단계가 맞는지 확인
    step = session.get("lost:step", None)
    if step is not None:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    # 폼에서 입력 받은 값 가져오기
    email = request.form.get("email", "")

    # 만약 이메일 주소에 '@'가 없다면
    if email.find("@") == -1:
        # 이메일 입력 화면으로 이동
        return redirect(url_for("dashboard.lost.step1"))

    # 입력 받은 이메일 주소로 유저 정보 데이터베이스에서 검색하기
    user = User.query.filter_by(
        email=email
    ).first()

    # 데이터베이스에 없는 유저라면
    if user is None:
        # 함정 모드 활성화하고 다음 단계로 이동
        session['password_lost'] = {
            "fake_mode": True,
        }

        # 이메일 보낸척 하기 위한 잠깐 멈추기
        sleep(0.005)
    else:
        # 데이터베이스에 있는 유저라면
        # 해당 이메일 주소로 인증토큰 보내고 다음 단계로 이동
        token = send(target_address=email)
        session['password_lost'] = {
            "user_idx": user.idx,
            "email": user.email,
            "token": token,
            "time": int(time())
        }

    # 비밀번호 초기화 단계 2단계로 설정하기
    session['lost:step'] = 2

    return redirect(url_for("dashboard.lost.step2"))


@bp.get("/step2")
def step2():
    # 비밀번호 초기화 단계가 2단계가 맞는지 확인
    step = session.get("lost:step", 1)
    if step != 2:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    return render_template(
        "dashboard/lost/step2.html"
    )


@bp.post("/step2")
def step2_post():
    # 비밀번호 초기화 단계가 2단계가 맞는지 확인
    step = session.get("lost:step", 1)
    if step != 2:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    # 1단계에서 입력 받은 정보 불러오기
    password_lost = session.get("password_lost", None)

    # 1단계에서 입력 받은 정보가 없다면
    if password_lost is None:
        # 비밀번호 초기화 단계 초기화하기
        del session['lost:step']

        # 1단계로 이동하기
        return redirect(url_for("dashboard.lost.step1"))

    # 함정 모드가 활성화 되어 있다면
    if password_lost.get("fake_mode", False):
        # 입력 폼으로 이동하기
        return redirect(url_for("dashboard.lost.step2"))

    # 입력 받은 토큰 불러오기
    token = request.form.get("token", "")

    # 입력 받은 토큰이 올바르지 않다면
    if token != password_lost['token']:
        # 입력 폼으로 이동하기
        return redirect(url_for("dashboard.lost.step2"))

    # 시간초과 확인하기
    if int(time()) - password_lost['time'] > 600:
        # 비밀번호 초기화 단계 초기화하기
        del session['lost:step']

        # 맨 처음 화면으로 이동하기
        return redirect(url_for("dashboard.lost.step1", why="timeout"))

    # 비밀번호 초기화 단계 3단계로 설정하기
    session['lost:step'] = 3

    return redirect(url_for("dashboard.lost.step3"))


@bp.get("/step3")
def step3():
    # 비밀번호 초기화 단계가 3단계가 맞는지 확인
    step = session.get("lost:step", 1)
    if step != 3:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    return render_template(
        "dashboard/lost/step3.html"
    )


@bp.post("/step3")
def step3_post():
    # 비밀번호 초기화 단계가 3단계가 맞는지 확인
    step = session.get("lost:step", 1)
    if step != 3:
        return redirect(url_for(f"dashboard.lost.step{step}"))

    # 1단계에서 입력 받은 정보 불러오기
    password_lost = session.get("password_lost", None)

    # 1단계에서 입력 받은 정보가 없다면
    if password_lost is None:
        # 비밀번호 초기화 단계 초기화하기
        del session['lost:step']

        # 1단계로 이동하기
        return redirect(url_for("dashboard.lost.step1"))

    # 입력받은 비밀번호 불러오기
    password = request.form.get("password", None)

    # 입력받은 비밀번호가 없거나 비밀번호가 8자리 보다 짧다면
    if password is None or len(password) < 8:
        # 입력 폼으로 이동하기
        return redirect(url_for("dashboard.lost.step3"))

    # 데이터베이스에서 유저 정보 불러오기
    user = User.query.filter_by(
        idx=password_lost['user_idx'],
        email=password_lost['email']
    ).first()

    # 유저 정보가 있다면
    if user is not None:
        # 입력 받은 비밀번호로 변경하기
        user.password = sha512(f"{password}+{SALT_PASSWORD}".encode()).hexdigest()
        db.session.commit()

    # 비밀번호 초기화관련해서 세션에 저장된 정보 삭제하기
    del session['lost:step']
    del session['password_lost']

    return redirect(url_for("dashboard.login.form"))
