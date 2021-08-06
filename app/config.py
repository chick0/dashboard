from os import environ
from secrets import token_bytes


# Session
SECRET_KEY = token_bytes(32)
SESSION_COOKIE_NAME = "s"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"


# SQLALCHEMY
SQLALCHEMY_DATABASE_URI = environ.get("dashboard_sql", default="sqlite:///dashboard.sqlite")
SQLALCHEMY_TRACK_MODIFICATIONS = False
