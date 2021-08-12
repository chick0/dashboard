from urllib.parse import urlparse

from flask import session


def is_two_factor_enabled() -> bool:
    two_factor = session.get("two_factor", None)
    if two_factor is None:
        return False

    return two_factor['status']


def is_two_factor_passed() -> bool:
    two_factor = session.get("two_factor", None)
    if two_factor is None:
        return False

    return two_factor['status'] == two_factor['passed']


def is_login(no_two_factor: bool = False) -> bool:
    login_user = session.get("user", None)
    if login_user is None:
        return False

    if no_two_factor:
        return True
    else:
        return is_two_factor_passed()


def url_verifier(url: str, fallback: str = "") -> str:
    url = urlparse(url=url)
    allow_schemes = [
        "http",
        "https",
    ]

    if url.scheme not in allow_schemes:
        return fallback

    return url.geturl()
