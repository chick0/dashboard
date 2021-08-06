
from flask import Blueprint
from flask import jsonify


bp = Blueprint(
    name="v1",
    import_name="v1",
    url_prefix="/v1"
)


@bp.get("")
def hello():
    return jsonify({
        "message": "Hello, World!"
    })
