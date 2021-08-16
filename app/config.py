from os import environ

from .secret_key import SECRET_KEY


# Session
SESSION_COOKIE_NAME = "s"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"


# SQLALCHEMY
SQLALCHEMY_DATABASE_URI = environ.get("dashboard_sql", default="sqlite:///dashboard.sqlite")
SQLALCHEMY_TRACK_MODIFICATIONS = False


# SMTP
SMTP_HOST = environ.get("dashboard_smtp_host", default="#")
SMTP_PORT = environ.get("dashboard_smtp_post", default="#")
SMTP_USER = environ.get("dashboard_smtp_user", default="#")
SMTP_PASSWORD = environ.get("dashboard_smtp_password", default="#")


# Password Salt
SALT_PASSWORD = environ.get("dashboard_salt_password", default="P6jpMNDh4nNT6Jchick0guJNRFyeNZBN")
