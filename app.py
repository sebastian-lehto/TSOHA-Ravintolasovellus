from flask import Flask
from flask import redirect, render_template, request, session
import os
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.secret_key = "9b761b17d8a5d34e763bd474e1c55e74"

app.config['SESSION_TYPE'] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uusi")
def uusi():
    return render_template("uusi.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["tunnus"]
    password = request.form["salasana"]

    session["username"] = username
    return redirect("/main")

@app.route("/main")
def main():
    result = db.session.execute("SELECT id, name, groups, ratings, rating, des FROM restaurants")
    rests = result.fetchall()
    return render_template("main.html", count=len(rests), rests = rests)
