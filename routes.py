import secrets
from app import app
from db import db
from sqlalchemy.sql import text
from flask import redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/")
def index():
    msg = "" if not "message" in request.args else request.args["message"]
    return render_template("index.html", message=msg)

@app.route("/new")
def new():
    msg = "" if not "message" in request.args else request.args["message"]
    return render_template("new.html", message=msg)

@app.route("/create",methods=["POST"])
def create():
    username = request.form["username"]
    password = request.form["password"]

    if not len(username) in range(4, 13) or not len(password) in range(4, 13):
                msg = "Username and Passwod must be 4-12 characters long!"
                return redirect(url_for("new", message=msg))

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
            session["csrf_token"] = secrets.token_hex(16)
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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/main")

        else:
            msg = "Invalid Password"
            return redirect(url_for("index", message=msg))
    
    else:
        msg = "Invalid Username"
        return redirect(url_for("index", message=msg))
    

@app.route("/restaurant/<id>",methods=['GET','POST'])
def restaurant(id):
    try :
        session["username"]
    except:    
        return redirect("/")
    
    sql1 = text("SELECT name, groups, ratings, rating, des FROM restaurants WHERE id=:id")
    sql2 = text("SELECT username, content, id FROM comments WHERE restaurant_id=:id")
    result1 = db.session.execute(sql1, {"id":id})
    result2 = db.session.execute(sql2, {"id":id})
    data = result1.fetchone()
    comments = result2.fetchall()
    msg = "" if not "message" in request.args else request.args["message"]
    return render_template("restaurant.html", data=data, id=id, comments=comments, message=msg)

@app.route("/rate", methods=["POST"])
def rate():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    
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

    comment = request.form["content"]
    if (len(comment) > 3):
        username = session["username"]
        sql3 = text("INSERT INTO comments (restaurant_id, username, content) VALUES (:id, :username, :comment)")
        db.session.execute(sql3, {"id":id, "username":username, "comment":comment})
        db.session.commit()

    msg = "Rating Added!"
    return redirect(url_for("restaurant", id=id, message=msg))

@app.route("/logout", methods=["POST"])
def logout():
    del session["username"]
    del session["csrf_token"]
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
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    name = request.form["name"]
    groups = request.form["groups"]
    des = request.form["desc"]
    sql = text("INSERT INTO restaurants (name, groups, ratings, rating, des) VALUES (:name, :groups, 0, 0, :des)")
    db.session.execute(sql, {"name":name, "groups":groups, "des":des})
    db.session.commit()

    return redirect("/main")

@app.route("/group", methods=["POST"])
def group():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

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
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    id = request.form["restaurant_id"]
    sql = text("DELETE FROM restaurants WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

    msg = "Restaurant Deleted!"
    return redirect(url_for('main', message=msg))

@app.route("/erase", methods=["POST"])
def erase():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    id = request.form["comment_id"]
    sql = text("DELETE FROM comments WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

    msg = "Comment Deleted!"
    restaurant_id = request.form["restaurant_id"]
    return redirect(url_for("restaurant", id=restaurant_id, message=msg))


