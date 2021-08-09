
from flask import Blueprint
from flask import redirect
from flask import url_for


bp = Blueprint(
    name="lost",
    import_name="lost",
    url_prefix="/lost"
)


@bp.get("/step1")
def step1():
    # TODO:이메일 입력받는 폼
    return ""


@bp.post("/step1")
def step1_post():
    # TODO:이메일 보내기
    # TODO:없는 계정이라면 이메일 보내지 않고 step2 로 이동

    return redirect(url_for("dashboard.lost.step2"))


@bp.get("/step2")
def step2():
    # TODO:이메일로 발송된 토큰 검증

    return ""


@bp.post("/step2")
def step2_post():
    # TODO:2단계 인증이 설정되어 있다면 한번 더 검증

    return redirect(url_for("dashboard.lost.step3"))


@bp.get("/step3")
def step3():
    # TODO:2단계 인증하기
    return ""


@bp.post("/step3")
def step3():
    return redirect(url_for("dashboard.lost.step4"))


@bp.get("/step4")
def step4():
    # TODO:새로운 비밀번호 입력받기
    return ""


@bp.post("/step4")
def step4_post():
    return redirect(url_for("dashboard.login.form"))
