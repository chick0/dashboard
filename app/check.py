
from flask import session


def is_two_factor_enabled() -> bool:
    two_factor = session.get("two_factor", None)
    if two_factor is None:
        return False

    return two_factor['status']


def is_login() -> bool:
    login_user = session.get("user", None)
    if login_user is None:
        return False

    two_factor = session.get("two_factor", None)
    if two_factor is None:
        return False

    if two_factor['status'] == two_factor['passed']:
        # False == False or True == True
        return True
    else:
        # True == False
        return False
