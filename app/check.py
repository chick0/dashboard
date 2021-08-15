from urllib.parse import urlparse

from flask import session

from app.models import User
from app.models import TwoFactor


def is_two_factor_enabled() -> bool:
    # 2단계 인증 정보 데이터베이스에서 검색하기
    two_factor = TwoFactor.query.filter_by(
        user_idx=session['user']['idx']
    ).first()

    # 검색결과가 있다면
    if two_factor is not None:
        # 활성화 상태
        return True
    else:
        # 비활성화 상태
        return False


def is_two_factor_passed() -> bool:
    # 세션에서 2단계 인증 정보 가져오기
    two_factor = session.get("two_factor", None)

    # 인증정보가 없다면
    if two_factor is None:
        # 통과한 상태가 아님
        return False

    # 2단계 인증이 활성화된 상태라면
    if is_two_factor_enabled():
        # 2단계 인증이 통과한 상황에만 통과로 인정
        return two_factor['passed']

    # 2단계 인증이 비활성화된 상태이므로 통과로 판정
    return True


def is_login(no_two_factor: bool = False) -> bool:
    # 세션에 저장된 유저 정보 불러오기
    login_user = session.get("user", None)

    # 저장된 값이 없다면
    if login_user is None:
        # 로그인 상태 아님
        return False

    # 데이터베이스에서 유저 정보 불러오기
    user = User.query.filter_by(
        idx=session['user']['idx']
    ).first()

    # 데이터베이스에서 발견된 유저 정보가 있다면
    if user is not None:
        # 세션에 저장된 유저 정보 업데이트 하기
        session['user'] = {
            "idx": user.idx,
            "email": user.email,
            "nickname": user.nickname,
        }
    else:
        # 세션에 저장된 모든 값 삭제하기
        for key in list(session.keys()):
            del session[key]

        # 로그인 상태 아님
        return False

    if no_two_factor:
        # 로그인 상태가 맞음
        return True
    else:
        # 2단계 인증을 통과했으면 로그인 상태가 맞음
        return is_two_factor_passed()


def url_verifier(url: str, fallback: str = "") -> str:
    # 검사할 URL 을 파싱하기
    url = urlparse(url=url)

    # 허용할 식별자 목록
    allow_schemes = [
        "http",
        "https",
    ]

    # 파싱한 URL 의 식별자가 허용하는 목록에 없다면
    if url.scheme not in allow_schemes:
        # 대체 값 리턴하기
        return fallback

    # 검사한 URL 리턴하기
    return url.geturl()
