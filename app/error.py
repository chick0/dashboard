
from flask import render_template
from flask import jsonify


def http400(err):
    return render_template("error/400.html"), 400


def http404(err):
    return render_template("error/404.html"), 404


def oauth_time_out(err):
    return render_template(
        "error/oauth_time_out.html"
    ), 400


def two_factor_required(err):
    return render_template(
        "error/two_factor_required.html"
    ), 400


def api_error_code_expired(err):
    return jsonify({
        "error": "this code is expired",
        "code": "api_error_code_expired"
    }), 408


def api_error_token_expired(err):
    return jsonify({
        "error": "this token is expired",
        "code": "api_error_token_expired"
    }), 408


def api_auth_fail(err):
    return jsonify({
        "error": "failed to get user from authentication data",
        "code": "api_auth_fail"
    }), 403


def api_invalid_application_secret_key(err):
    return jsonify({
        "error": "invalid application secret key",
        "code": "api_invalid_application_secret_key"
    }), 403


def api_error_app_not_found(err):
    return jsonify({
        "error": "failed to get application from database. maybe this application is deleted.",
        "code": "api_error_app_not_found"
    }), 404


def api_error_user_not_found(err):
    return jsonify({
        "error": "failed to get user from database",
        "code": "api_error_user_not_found"
    }), 404
