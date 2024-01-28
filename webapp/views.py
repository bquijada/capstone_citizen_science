from urllib.parse import quote_plus, urlencode
from auth.decorators import requires_auth
from flask import Blueprint, redirect, session, url_for, current_app
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template

auth_bp = Blueprint('auth', __name__)
webapp_bp = Blueprint('webapp', __name__)

@webapp_bp.route("/")
def home():
    """
    """
    return render_template('index.html')

@webapp_bp.route("/test")
def test():
    """
    """
    return "test"

@webapp_bp.route("/profile")
@requires_auth
def profile():
    """
    Unprotected endpoint which displays your profile if you are logged in, otherwise it prompts the user to log in
    """

    return session.get('user').get("userinfo")
