
from flask import Blueprint

from app import api


bp = Blueprint(
    name="api",
    import_name="api",
    url_prefix="/api"
)


# 여기는 API 버전 넘겨주는 블루프린트
# 진짜 API 코드는 app/api/{api_version} 에다가 작성하기
for api_version in api.__all__:
    bp.register_blueprint(getattr(getattr(getattr(__import__(f"app.api.{api_version}"), "api"), api_version), "bp"))
