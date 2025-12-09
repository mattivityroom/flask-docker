# app.py
from flask import Flask, request, url_for
from markupsafe import escape

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "<h1>Hello from Flask in a Docker container!</h1>"

@app.get('/login')
def login():
    test = request.args.get("name", "Flask")
    return f"Hello, {escape(test)}!"

@app.route('/user/<string:username>')
def user_detail(username):
    return f"{escape(username.capitalize())}'s user profile!"

@app.route('/path/<path:subpath>')
def show_path(subpath):
    return f"Subpath {escape(subpath)}"

with app.test_request_context():
    print(url_for('hello'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('user_detail', username='John Doe'))
    print(url_for('show_path', subpath='a/b/c'))