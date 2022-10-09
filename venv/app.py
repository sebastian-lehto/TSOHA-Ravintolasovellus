from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.secret_key = getenv(SECTER_KEY)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uusi")
def uusi():
    return render_template("uusi.html")

@app.route("/login")
def login():
    usr = request.form["tunnus"]
    usr = request.form["salasana"]

    session["username"] = usr
    return redirect("/main")

@app.route("/main")
def main():
    result = db.session.execute("SELECT id, name, groups, ratings, rating, des FROM restaurants")
    rests = result.fetchall()
    return render_template("main.html", count=len(rests), rests = rests)
