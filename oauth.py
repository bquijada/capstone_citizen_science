import json

import os
import flask
import requests


app = flask.Flask(__name__)

CLIENT_ID = '1047223923378-lh9bc8lk0m64ptufq7hhof76fi5vsjg2.apps.googleusercontent.com'
CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # Read from a file or environmental variable in a real app
SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'
REDIRECT_URI = 'http://127.0.0.1:5000'


@app.route('/login')
def index():
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
    return flask.redirect(auth_uri)


@app.route('/')
def home():
  if 'code' not in flask.request.args:
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
    return flask.redirect(auth_uri)
  else:
    return "logged in"


if __name__ == '__main__':

  app.debug = False
  app.run()