
from flask import request


def get_ip() -> str:
    for header in [
        "CF-Connecting-IP",  # 클라우드플레어에서 전달받은 IP 주소 값
        "X-Forwarded-For",   # 리버스 프록시 서버에서 전달받은 IP 주소 값
    ]:
        tmp = request.headers.get(header, "")

        # IP 주소가 7자 보다 길고 127.0.0.1 이 아니라면
        if len(tmp) >= 7 and tmp != "127.0.0.1":
            # 비표준 헤더에서 가져온 IP 주소 값 리턴하기
            return tmp

    # IP 정보를 저장하고 있는 비표준 헤더가 없다면 표준 헤더에서 가져오기
    return request.remote_addr
