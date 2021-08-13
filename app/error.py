

from flask import render_template


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
