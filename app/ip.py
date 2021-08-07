
from flask import request


def get_ip() -> str:
    for header in [
        "CF-Connecting-IP",
        "X-Forwarded-For",
    ]:
        tmp = request.headers.get(header, "")
        if len(tmp) >= 7 and tmp != "127.0.0.1":
            return tmp

    return request.remote_addr
