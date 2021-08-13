
from .error import *


class OAuthTimeOut(Exception):
    def __init__(self):
        super().__init__()


class TwoFactorRequired(Exception):
    def __init__(self):
        super().__init__()


error_map = {
    400: http400,
    404: http404,

    OAuthTimeOut: oauth_time_out,
    TwoFactorRequired: two_factor_required,
}
