# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello from Flask in a Docker container!</h1>"