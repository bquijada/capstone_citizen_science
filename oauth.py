

from flask_oidc import OpenIDConnect
from flask import Flask, render_template

from auth.views import auth_bp
from webapp.views import webapp_bp

import json
import os
import flask
import requests


"""@app.route('/')
def home():
  if 'code' not in flask.request.args:
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
    return flask.redirect(auth_uri)
  else:
    return "logged in"""

def create_app():
    """
    Configuration of the app
    """
    app = Flask(__name__)

    app.secret_key = os.getenv("SECRET_KEY") # 👈 new code


    app.register_blueprint(auth_bp, url_prefix='/') # 👈 new code
    app.register_blueprint(webapp_bp, url_prefix='/')

    return app


if __name__ == '__main__':

    app = create_app()
    app.run()