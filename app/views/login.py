
from flask import Blueprint
from flask import render_template


bp = Blueprint(
    name="login",
    import_name="login",
    url_prefix="/login"
)


@bp.get("")
def form():
    return render_template(
        "dashboard/login/form.html"
    )


@bp.get("/2fa")
def verify_2fa():
    return render_template(
        "dashboard/login/2fa.html"
    )


@bp.get("/email")
def verify_email():
    return render_template(
        "dashboard/login/email.html"
    )
