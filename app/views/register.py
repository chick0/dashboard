
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import render_template


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
    return render_template(
        "dashboard/register/step1.html"
    )


@bp.get("/step2")
def step2():
    return render_template(
        "dashboard/register/step2.html"
    )
