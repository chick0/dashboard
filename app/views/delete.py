
from flask import Blueprint


bp = Blueprint(
    name="delete",
    import_name="delete",
    url_prefix="/delete"
)


@bp.get("/ask")
def ask():
    # TODO:회원탈퇴 물어보기
    # TODO:생성한 어플이 있으면 탈퇴 취소

    return "todo"
