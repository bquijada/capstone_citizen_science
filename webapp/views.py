from urllib.parse import quote_plus, urlencode
from auth.decorators import requires_auth
from flask import Blueprint, redirect, session, url_for, current_app
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, request

webapp_bp = Blueprint('webapp', __name__)


@webapp_bp.route("/")
def home():
    """
    Homepage endpoint
    """
    return render_template('index.html')

@webapp_bp.route("/profile")
@requires_auth
def profile():
    """
    Unprotected endpoint which displays your profile if you are logged in, otherwise it prompts the user to log in
    """
    userinfo = session.get('user').get("userinfo")
    access_token = session.get('user').get("access_token")
    data = {
        'userinfo': userinfo,
        'access_token': access_token
    }
    session.get('user').get("access_token")

    return data

@webapp_bp.route("/view_created_project")
def create_project():
    _title = request.args.get('title')
    _code = request.args.get('code')
    _description = request.args.get('code')
    return render_template('project.html', title =_title, description = _description, code = _code)