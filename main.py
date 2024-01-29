
from flask import Flask, render_template

from auth.views import auth_bp
from webapp.views import webapp_bp

import json
import os
import flask
import requests

app = Flask(__name__)

app.secret_key = "1234567890"
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(webapp_bp, url_prefix='/')




if __name__ == '__main__':

    """host='127.0.0.1', port=8080, debug=True"""
    app.run()

