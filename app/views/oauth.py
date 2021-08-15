from uuid import uuid4
from time import time
from secrets import token_bytes

from flask import Blueprint
from flask import abort
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Application
from app.models import Code
from app.models import Token
from app.check import is_login
from app.custom_error import OAuthTimeOut


bp = Blueprint(
    name="oauth",
    import_name="oauth",
    url_prefix="/oauth"
)


@bp.get("")
def ask():
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    try:
        app_id = int(request.args.get("app_id", "None"))
        if app_id <= 0:
            return abort(400)
    except ValueError:
        return abort(400)

    app = Application.query.filter_by(
        idx=app_id
    ).first()
    if app is None:
        return abort(404)

    scope = request.args.get("scope", "id")

    key = uuid4().__str__()
    session[f"oauth:{key}"] = {
        "app_id": app.idx,
        "scope": scope,
        "user_id": session['user']['idx'],
        "time": int(time())
    }

    return render_template(
        "oauth/ask.html",
        app=app,
        scope=scope,
        key=key
    )


@bp.get("/<string:key>")
def callback(key: str):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    oauth_data = session.get(f"oauth:{key}", None)
    if oauth_data is None:
        return abort(400)

    if int(time()) - oauth_data['time'] >= 300:
        raise OAuthTimeOut

    app = Application.query.filter_by(
        idx=oauth_data['app_id']
    ).first()
    if app is None:
        return abort(404)

    code = Code()
    code.application_idx = app.idx
    code.target_idx = oauth_data['user_id']
    code.scope = oauth_data['scope']
    code.code = token_bytes(16).hex()

    db.session.add(code)
    db.session.commit()

    del session[f"oauth:{key}"]
    return redirect(app.callback + f"?code={code.code}")


@bp.get("/revoke/<string:app_idx>")
def revoke(app_idx: str):
    if not is_login():
        return redirect(url_for("dashboard.login.form"))

    Token.query.filter_by(
        application_idx=app_idx,
        target_idx=session['user']['idx']
    ).delete()

    db.session.commit()

    return redirect(url_for("dashboard.application.show_all"))
