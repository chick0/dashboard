
from flask import Blueprint


bp = Blueprint(
    name="application",
    import_name="application",
    url_prefix="/application"
)


@bp.get("")
def show_all():
    # TODO:내가 로그인한 어플리케이션 목록 보여주기

    return "todo"


@bp.get("/my")
def my():
    # TODO:내가 만든 어플리케이션 목록 보여주기

    return "todo"


@bp.get("/register")
def register():
    # TODO:앱 등록하기

    return "todo"


@bp.get("/detail/<string:app_idx>")
def detail(app_idx):
    # TODO:앱 아이디를 가지고 있는 어플리케이션 정보를 보여주기

    return f"todo : {app_idx}"
