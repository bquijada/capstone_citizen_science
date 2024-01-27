from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
