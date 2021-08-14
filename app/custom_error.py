
from .error import *


class OAuthTimeOut(Exception):
    def __init__(self):
        super().__init__()


class TwoFactorRequired(Exception):
    def __init__(self):
        super().__init__()


class ApiErrorCodeExpired(Exception):
    def __init__(self):
        super().__init__()


class ApiErrorTokenExpired(Exception):
    def __init__(self):
        super().__init__()


class ApiAuthFail(Exception):
    def __init__(self):
        super().__init__()


class ApiApplicationSecretInvalid(Exception):
    def __init__(self):
        super().__init__()


class ApiErrorAppNotFound(Exception):
    def __init__(self):
        super().__init__()


class ApiErrorUserNotFound(Exception):
    def __init__(self):
        super().__init__()


error_map = {
    400: http400,
    404: http404,

    OAuthTimeOut: oauth_time_out,
    TwoFactorRequired: two_factor_required,
    ApiErrorCodeExpired: api_error_code_expired,
    ApiErrorTokenExpired: api_error_token_expired,
    ApiAuthFail: api_auth_fail,
    ApiApplicationSecretInvalid: api_invalid_application_secret_key,
    ApiErrorAppNotFound: api_error_app_not_found,
    ApiErrorUserNotFound: api_error_user_not_found,
}
