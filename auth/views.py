from flask import Blueprint, redirect, session, url_for, current_app
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template
import os

auth_bp = Blueprint('auth', __name__)


oauth = OAuth(current_app)
CLIENT_ID="xm0b7wYkKdz7dtc0XsecmO8z5BPCMFrf"
CLIENT_SECRET="33rY21_EpoVNkXSyky5hoR0UFjrpq8feQUz9Nt6J6xUto5kOcol2LOVUhklAQvzn"
DOMAIN="leungp.us.auth0.com"
domain = "leungp.us.auth0.com"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

oauth.register(
   'auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_base_url="https://" + domain,
    access_token_url="https://" + domain + "/oauth/token",
    authorize_url="https://" + domain + "/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
)


@auth_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """
    Callback redirect from Auth0
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    # The app assumes for a /profile path to be available, change here if it's not
    return redirect("/profile")

@auth_bp.route("/login")
def login():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )

@auth_bp.route("/logout")
def logout():
    """
    Logs the user out of the session and from the Auth0 tenant
    """
    session.clear()
    return render_template('index.html')

@auth_bp.route("/signup")
def signup():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        screen_hint="signup"
    )

@auth_bp.route("/test2")
def test2():
    return "test2"