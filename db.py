from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app.secret_key = getenv("SECRET_KEY")

app.config['SESSION_TYPE'] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
db = SQLAlchemy(app)