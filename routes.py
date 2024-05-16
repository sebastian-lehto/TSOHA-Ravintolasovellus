from app import app
from db import db
from sqlalchemy.sql import text
from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/")
def index():
    msg = "" if not "message" in request.args else request.args["message"]
    return render_template("index.html", message=msg)

@app.route("/new")
def uusi():
    return render_template("new.html")

@app.route("/create",methods=["POST"])
def luo():
    username = request.form["username"]
    password = request.form["password"]

    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    session["username"] = username
    return redirect("/main")



@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql1 = text("SELECT id, password FROM users WHERE username=:username")
    sql2 = text("SELECT id, password FROM admins WHERE username=:username")
    result1 = db.session.execute(sql1, {"username":username})
    result2 = db.session.execute(sql2, {"username":username})
    user = result1.fetchone()
    admin = result2.fetchone()    
    if admin:
        hash_value = admin.password
        if check_password_hash(hash_value, password):
            session["username"] = "admin"
            return redirect("/main")
        else:
            msg = "Invalid Password"
            return redirect(url_for("index", message=msg))
    elif user:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            if username == "admin": 
                username = "USER"
            session["username"] = username
            return redirect("/main")
        else:
            msg = "Invalid Password"
            return redirect(url_for("index", message=msg))
    else:
        msg = "Invalid Username"
        return redirect(url_for("index", message=msg))
    return redirect("/")  
    

@app.route("/restaurant/<id>",methods=['GET','POST'])
def restaurant(id):
    try :
        session["username"]
    except:    
        return redirect("/")
    
    sql = text("SELECT name, groups, ratings, rating, des FROM restaurants WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    data = result.fetchone()
    return render_template("restaurant.html", data=data, id=id)

@app.route("/rate", methods=["POST"])
def rate():
    id = request.form["restaurant_id"]
    sql = text("SELECT ratings, rating FROM restaurants WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    data = result.fetchone()
    
    amnt = data[0]
    cur = data[1]
    rat = int(request.form["rating"])
    new = ((amnt * cur) + rat) / (amnt + 1)
    amnt = amnt + 1
    sql1 = text("UPDATE restaurants SET ratings = ':amnt' WHERE id=:id")
    sql2 = text("UPDATE restaurants SET rating = ':new' WHERE id=:id")
    db.session.execute(sql1, {"amnt":amnt, "id":id})
    db.session.execute(sql2, {"new":new, "id":id})
    db.session.commit()

    msg = "Rating Added!"
    return redirect(url_for('main', message=msg))

@app.route("/logout", methods=["POST"])
def logout():
    del session["username"]
    return redirect("/")

@app.route("/back", methods=["POST"])
def back():
    return redirect("/main")


@app.route("/main")
def main():
    try :
        session["username"]
    except:    
        return redirect("/")
    sql = text("SELECT id, name, groups, ratings, rating, des FROM restaurants ORDER BY rating DESC")
    result = db.session.execute(sql)
    rests = result.fetchall()

    msg = "" if not "message" in request.args else request.args["message"]
    return render_template("main.html", count=len(rests), rests = rests, message=msg)

@app.route("/search", methods=["POST"])
def search():
    word = "%" + request.form["search"] + "%"
    sql = text("SELECT id, name, groups, ratings, rating, des FROM restaurants WHERE groups LIKE :word OR des LIKE :word ORDER BY rating DESC")
    result = db.session.execute(sql, {"word":word})
    rests = result.fetchall()

    return render_template("main.html", count=len(rests), rests = rests)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    groups = request.form["groups"]
    des = request.form["desc"]
    sql = text("INSERT INTO restaurants (name, groups, ratings, rating, des) VALUES (:name, :groups, 0, 0, :des)")
    db.session.execute(sql, {"name":name, "groups":groups, "des":des})
    db.session.commit()

    return redirect("/main")

@app.route("/group", methods=["POST"])
def group():
    id = request.form["restaurant_id"]
    groups = request.form["group"]
    
    if not groups.strip():
        return redirect("/main")
    
    sql1 = text("SELECT groups FROM restaurants WHERE id=:id")
    result = db.session.execute(sql1, {"id":id})
    old = result.fetchone()
    new = old[0] + "," + groups
    sql2 = text("UPDATE restaurants SET groups = :new WHERE id=:id")
    db.session.execute(sql2, {"new":new, "id":id})
    db.session.commit()

    msg = "Group Added!"
    return redirect(url_for('main', message=msg))

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form["restaurant_id"]
    sql = text("DELETE FROM restaurants WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

    msg = "Restaurant Deleted!"
    return redirect(url_for('main', message=msg))

