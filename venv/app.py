from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/main", methods=["POST"])
def main():
    return render_template("main.html")
