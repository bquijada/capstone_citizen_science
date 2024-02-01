from flask import Blueprint, redirect, session, url_for, current_app
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template
import os
from google.cloud import datastore
import requests

client = datastore.Client()
auth_bp = Blueprint('auth', __name__)


oauth = OAuth(current_app)
CLIENT_ID = "xm0b7wYkKdz7dtc0XsecmO8z5BPCMFrf"
CLIENT_SECRET = "33rY21_EpoVNkXSyky5hoR0UFjrpq8feQUz9Nt6J6xUto5kOcol2LOVUhklAQvzn"
DOMAIN = "leungp.us.auth0.com"

oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_base_url="https://" + DOMAIN,
    access_token_url="https://" + DOMAIN + "/oauth/token",
    authorize_url="https://" + DOMAIN + "/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{DOMAIN}/.well-known/openid-configuration'
)


@auth_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """
    Callback redirect from Auth0
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token

    # Get user information from Auth0 userinfo endpoint
    userinfo_url = f'https://{DOMAIN}/userinfo'
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = requests.get(userinfo_url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        user_id = user_info.get('sub')  # 'sub' is the user ID in Auth0
        user_name = user_info.get('name')
        user_email = user_info.get('email')
        print(user_name, user_email, user_id)
    else:
        return 'Failed to get user information from Auth0', 500
    # add user to database in not already added
    query = client.query(kind="users")
    query.add_filter("user", "=", user_id)
    result = list(query.fetch())
    if not result:
        new_user = datastore.entity.Entity(key=client.key("users"))
        new_user.update({"user": user_id, "name": user_name, "email": user_email})
        client.put(new_user)
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
