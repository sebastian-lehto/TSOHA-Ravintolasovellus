from app import app
from db import db
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uusi")
def uusi():
    return render_template("uusi.html")

@app.route("/luo",methods=["POST"])
def luo():
    username = request.form["tunnus"]
    password = request.form["salasana"]

    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    session["username"] = username
    return redirect("/main")



@app.route("/login",methods=["POST"])
def login():
    username = request.form["tunnus"]
    password = request.form["salasana"]

    sql1 = "SELECT id, password FROM users WHERE username=:username"
    sql2 = "SELECT id, password FROM admins WHERE username=:username"
    result1 = db.session.execute(sql1, {"username":username})
    result2 = db.session.execute(sql2, {"username":username})
    user = result1.fetchone()
    admin = result2.fetchone()    
    if not user:
        return redirect("/")
        # TODO: invalid username
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            if admin:
                session["username"] = "admin"
                return redirect("/main")
            else:
                if username == "admin": 
                    username = "USER"
                session["username"] = username
                return redirect("/main")
        else:
            return redirect("/")
            # TODO: invalid password  
    return redirect("/")  
    

@app.route("/ravintola/<id>",methods=['GET','POST'])
def ravintola(id):
    try :
        session["username"]
    except:    
        return redirect("/")
    
    sql = "SELECT name, groups, ratings, rating, des FROM restaurants WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    data = result.fetchone()
    return render_template("ravintola.html", data=data, id=id)

@app.route("/rate", methods=["POST"])
def rate():
    id = request.form["tunnus"]
    sql = "SELECT ratings, rating FROM restaurants WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    data = result.fetchone()
    
    amnt = data[0]
    cur = data[1]
    rat = int(request.form["arvosana"])
    new = ((amnt * cur) + rat) / (amnt + 1)
    amnt = amnt + 1
    sql1 = "UPDATE restaurants SET ratings = ':amnt' WHERE id=:id"
    sql2 = "UPDATE restaurants SET rating = ':new' WHERE id=:id"
    db.session.execute(sql1, {"amnt":amnt, "id":id})
    db.session.execute(sql2, {"new":new, "id":id})
    db.session.commit()

    return redirect("/main")

@app.route("/logout", methods=["POST"])
def logout():
    del session["username"]
    return redirect("/")


@app.route("/main")
def main():
    try :
        session["username"]
    except:    
        return redirect("/")
    result = db.session.execute("SELECT id, name, groups, ratings, rating, des FROM restaurants ORDER BY rating DESC")
    rests = result.fetchall()
    return render_template("main.html", count=len(rests), rests = rests)

@app.route("/search", methods=["POST"])
def search():
    word = "%" + request.form["search"] + "%"
    sql = "SELECT id, name, groups, ratings, rating, des FROM restaurants WHERE groups LIKE :word OR des LIKE :word ORDER BY rating DESC"
    result = db.session.execute(sql, {"word":word})
    rests = result.fetchall()

    return render_template("main.html", count=len(rests), rests = rests)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    groups = request.form["groups"]
    des = request.form["desc"]
    sql = "INSERT INTO restaurants (name, groups, ratings, rating, des) VALUES (:name, :groups, 0, 0, :des)"
    db.session.execute(sql, {"name":name, "groups":groups, "des":des})
    db.session.commit()

    return redirect("/main")

@app.route("/group", methods=["POST"])
def group():
    id = request.form["tunnus"]
    groups = request.form["group"]
    
    if not groups.strip():
        return redirect("/main")
    
    sql1 = "SELECT groups FROM restaurants WHERE id=:id"
    result = db.session.execute(sql1, {"id":id})
    old = result.fetchone()
    new = old[0] + "," + groups
    sql2 = "UPDATE restaurants SET groups = :new WHERE id=:id"
    db.session.execute(sql2, {"new":new, "id":id})
    db.session.commit()

    return redirect("/main")

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form["tunnus"]
    sql = "DELETE FROM restaurants WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

    return redirect("/main")

