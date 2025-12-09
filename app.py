# app.py
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello from Flask in a Docker container!</h1>"

# HTML Escaping
@app.route('/login')
def login():
    test = request.args.get("name", "Flask")
    return f"Hello, {escape(test)}!"

@app.route('/user/<string:username>')
def user_detail(username):
    return f"Hello, {escape(username)}!"

@app.route('/path/<path:subpath>')
def show_path(subpath):
    return f"Subpath {escape(subpath)}"