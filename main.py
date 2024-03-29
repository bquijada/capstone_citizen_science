from datetime import timedelta
from flask import Flask, render_template
from auth.views import auth_bp
from webapp.views import webapp_bp
from datastore.endpoints import datastore_bp

import json
import os
import flask
import requests

app = Flask(__name__)

app.secret_key = "1234567890"

# Set session permanency
app.permanent_session_lifetime = timedelta(days=1)
app.permanent_session = True

app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(webapp_bp, url_prefix='/')
app.register_blueprint(datastore_bp, url_prefix='/')



if __name__ == '__main__':

    """host='127.0.0.1', port=8080, debug=True"""
    app.run(debug=True)

