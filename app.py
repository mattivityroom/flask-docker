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