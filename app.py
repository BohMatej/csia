import os
import sys
sys.path.append("mhdle_src")
from flask import Flask, redirect, render_template, request, session, url_for, jsonify, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json
from helpers import login_required, admin_required, query_database
from routegeneration import generateRoute, verifyRoute
from routehelpers import unpackStops

DIRNAME = os.path.dirname(__file__)

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return redirect("/custom")


@app.route('/custom', methods=["GET", "POST"])
def custom():
    if request.method == "POST":
        if request.form.get("usegreylines") is None:
            ugl = False
        else:
            ugl = True

        route = generateRoute(
            length=int(request.form.get("btnroute")),
            area=tuple(request.form.getlist("area")),
            useGreyLines=ugl
        )
        
        data = {
            "gamemode": "custom",
            "availablelines": sorted(route.generateFirstLines(), key=len),
            "linelist": route.data.linelist,
            "stoplist": unpackStops(route.data.stoplist),
            "passedstoplist": [unpackStops(stops) for stops in route.data.passedstoplist],
            "walkingtransferlist": [[unpackStops(transfers[0]), transfers[1]] if transfers is not None else None for transfers in route.data.walkingtransferlist],
            "interlinedlist": route.data.interlinedlist,
            "useGreyLines": ugl,
            "numberOfGuessesRaw": request.form.get("btnguess")
        }
        
        route.printRoute()
        
        return render_template(
            "customgame.html", 
            data=json.dumps(data, indent=4)
        )
    else:
        return render_template("custommenu.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return "Username was not submitted."

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "Password was not sumbitted."

        # Query database for username
        # rows = db.execute(
        #     "SELECT * FROM users WHERE username = ?", request.form.get("username")
        # )
        rows = query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"), 
            "SELECT user_id, hashed_password FROM users WHERE username = ?", 
            (request.form.get("username"),)
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][1], request.form.get("password")
        ):
            return "Username or password are incorrect."

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return "Password and confirmation do not match"

        # Ensure confirmation is the same as password
        elif request.form.get("confirmation") != request.form.get("password"):
            return "Password and confirmation do not match"

        # Query database for username
        # rows = db.execute(
        #     "SELECT * FROM users WHERE username = ?", request.form.get("username")
        # )
        rows = query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "SELECT user_id, username FROM users WHERE username = ?", 
            (request.form.get("username"),)
        )

        # Ensure username does not exist
        if len(rows) >= 1:
            return "username already exists"

        # hash password
        hashed_password = generate_password_hash(request.form.get("password"))

        # add registered user to database
        query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "INSERT INTO users (username, hashed_password, time_of_creation) VALUES (?, ?, datetime('now'))",
            (request.form.get("username"), hashed_password)
        )

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """Changes password"""

    if request.method == "POST":
        # Ensure old password is submitted
        if not request.form.get("old_password"):
            return "must provide username"

        # Ensure new password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return "Password and confirmation do not match"

        # Ensure old password is correct
        if not check_password_hash(
            query_database(
                os.path.join(DIRNAME, "database/mhdle_private.db"),
                "SELECT hashed_password FROM users WHERE user_id = ?",
                (session["user_id"],)
            )[0][0],
            request.form.get("old_password")
        ):
            "Password does not match current password"

        # Ensure confirmation is the same as password
        elif request.form.get("confirmation") != request.form.get("password"):
            return "Password and confirmation do not match"

        # hash password
        hashed_password = generate_password_hash(request.form.get("password"))

        # update user's password in the database
        query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "UPDATE users SET hashed_password = ? WHERE user_id = ?",
            (hashed_password, session["user_id"])
        )

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("change_password.html")
    
@app.route("/admin-daily", methods=["GET", "POST"])
@admin_required
def admin_daily():
    if request.method == "POST":
        req = request.get_json()
        # print("HERE")
        # print(req)
        # print(req["linelist"])
        raw = query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "SELECT routedate FROM dailyroutes WHERE routedate >= DATE('now') ORDER BY routedate DESC",
            False
        )

        if len(raw) == 0:
            query_database(
                os.path.join(DIRNAME, "database/mhdle_private.db"),
                "INSERT INTO dailyroutes (routejson, routedate) VALUES (?, DATE('now'))",
                (json.dumps(req),)
            )
        else:
            dates = [obj[0] for obj in raw]
            print(dates)
        
        raw = query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "SELECT routejson, routedate, route_id FROM dailyroutes WHERE routedate >= DATE('now') ORDER BY routedate DESC",
            False
            )
        if len(raw) != 0:
            jsonobject = [{"routejson": json.loads(obj[0]), "routedate": obj[1], "route_id": obj[2]} for obj in raw]
        else:
            jsonobject = 0
        
        return make_response(jsonify(jsonobject), 200)
            
    else:
        raw = query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "SELECT routejson, routedate, route_id FROM dailyroutes WHERE routedate >= DATE('now') ORDER BY routedate DESC",
            False
            )
        if len(raw) != 0:
            #print(raw)
            jsonobject = [{"routejson": json.loads(obj[0]), "routedate": obj[1], "route_id": obj[2]} for obj in raw]
        else:
            jsonobject = 0
        
        #print(jsonobject)
        data = json.dumps(jsonobject, indent=4)
        print(data)
        
        return render_template("admindaily.html", data = data)

# @app.route("/admin-writedailyroute")
# @admin_required
# def admin_writeDailyRoute():
#     req = 
    

@app.route('/verifyroute', methods=["POST"])
def verifyroute():
    req = request.get_json()
    print(req["lines"])
    lines = tuple(req["lines"])

    myroute = verifyRoute(lines) # buggy

    if myroute is None:
        res = {"message": "Invalid"}
    else:
        res = {"message": "Valid"}
        
    print(res)
    
    out = make_response(jsonify(res), 200)
    return out

@app.route('/generateDailyRoute', methods=["POST"])
def generateDailyRoute():
    route = generateRoute()
    data = {
        "gamemode": "daily",
        "availablelines": sorted(route.generateFirstLines(), key=len),
        "linelist": route.data.linelist,
        "stoplist": unpackStops(route.data.stoplist),
        "passedstoplist": [unpackStops(stops) for stops in route.data.passedstoplist],
        "walkingtransferlist": [[unpackStops(transfers[0]), transfers[1]] if transfers is not None else None for transfers in route.data.walkingtransferlist],
        "interlinedlist": route.data.interlinedlist,
    }
    
    out = make_response(jsonify(data), 200)
    return out

with app.test_request_context():
    print("Hello")