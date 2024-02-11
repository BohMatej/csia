import os
import sys
import csv
sys.path.append("mhdle_src")
from flask import Flask, redirect, render_template, request, session, url_for, jsonify, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
from helpers import unpackStops, login_required, admin_required, daily_not_beaten_required, query_database, find_missing_consecutive_date, date_streaks
from routegeneration import generateRoute, verifyRoute
sys.path.append("database")
from dbupdate import DatabaseUpdate


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
UPLOAD_FOLDER = 'static/line_icons'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DIRNAME = os.path.dirname(__file__)

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

@app.route('/daily')
@login_required
# @daily_not_beaten_required
def daily():
    
    rawdata = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "SELECT routejson FROM dailyroutes WHERE routedate = DATE('now')",
        False
    )[0][0]
    
    data = json.loads(rawdata)
    data["useGreyLines"] = False
    data["numberOfGuessesRaw"] = 0
    
    rawprogress = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """SELECT route_order, labelone, labeltwo, labelthree
        FROM solution_progress_table
        WHERE user_id = ? AND routedate = DATE('now')
        ORDER BY route_order ASC""",
        (session["user_id"],)
    )
    return render_template(
        "dailymhdle.html", 
        data=json.dumps(data, indent=4),
        progress=json.dumps(rawprogress, indent=4)
    )

    

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

@app.route("/admin-servicemod", methods=["GET", "POST"])
@admin_required
def admin_servicemod():
    if request.method == "POST":
        pass
    else:
        rawlines = query_database(
            os.path.join(DIRNAME, "database/mhdle.db"),
            "SELECT label, looping_status, color FROM lines",
            False
        )
        rawstops = query_database(
            os.path.join(DIRNAME, "database/mhdle.db"),
            "SELECT stop_id, district, truename FROM stops ORDER BY truename",
            False
        )
        rawnearstops = query_database(
            os.path.join(DIRNAME, "database/mhdle.db"),
            "SELECT nearstops_id, stopone_id, stoptwo_id, walktime FROM nearstops",
            False
        )
        lines = dict()
        for line in rawlines:
            subservices = dict()
            rawservices = query_database(
                os.path.join(DIRNAME, "database/mhdle.db"),
                """SELECT services_id, stop_id, subservice, order_in_subservice 
                FROM services WHERE line_label = ?
                ORDER BY subservice, order_in_subservice""",
                (line[0],)
            )
            currentSubservice = 0
            for rawservice in rawservices:
                if rawservice[2] > currentSubservice:
                    currentSubservice += 1
                    subservices[currentSubservice] = list()
                subservices[currentSubservice].append(rawservice[1])
                
            lines[line[0]] = {"label": line[0], "looping_status": line[1], "color": line[2], "service": subservices}
        #print(lines)
        #lines = [{"label": line[0], "looping_status": line[1], "color": line[2]} for line in rawlines]
        
        stops = dict()
        for stop in rawstops:
            stops[stop[0]] = {"district": stop[1], "truename": stop[2]}
            
        #stops = [{"stop_id": line[0], "district": line[1], "truename": line[2]} for line in rawstops]
        nearstops = [{"nearstops_id": line[0], "stopone_id": line[1], "stoptwo_id": line[2], "walktime": line[3]} for line in rawnearstops]
        return render_template("adminroute.html", 
                               lines=json.dumps(lines, indent=4), 
                               stops=json.dumps(stops, indent=4), 
                               nearstops=json.dumps(nearstops, indent=4)
        )
        
@app.route("/admin-save-servicemod", methods=["POST"])
@admin_required
def admin_save_servicemod():
    req = request.get_json()
    loopers=[]
    
    # services
    with open("database/data/services.txt", "w") as file:
        for label in req["lines"]:
            file.write(f"/line {label} {{\n")
            if req['lines'][str(label)]['color'] != '9e9e9e':    
                file.write(f"    /color {req['lines'][str(label)]['color']}\n")
            if req['lines'][str(label)]['looping_status'] != 0:
                loopers.append(label)  
            for subservice in req['lines'][str(label)]['service']:
                file.write(f"    /subservice {subservice} [\n")
                for stopid in req['lines'][str(label)]['service'][subservice]:
                    file.write(f"        {stopid}\n")
                file.write("    ]\n")
            file.write("}\n")
            file.write("\n")
    
    # loops
    with open("database/data/loops.csv", "w", newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(["alias", "looptype"])
        for stopid in loopers:
            csvwriter.writerow([stopid, 1])
    
    # stops
    with open("database/data/stops.csv", "w", newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(["uid", "district", "truename"])
        for stop in req['stops']:
            csvwriter.writerow([stop, req['stops'][stop]['district'], req['stops'][stop]['truename']])
            
    # nearstops
    with open("database/data/nearstops.csv", "w", newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(["first", "second", "walktime"]) 
        for nearstops in req['nearstops']:
            csvwriter.writerow([nearstops['stopone_id'], nearstops['stoptwo_id'], nearstops['walktime']])
    
    DatabaseUpdate.updateStopsDatabase()
    DatabaseUpdate.updateAllDatabase()
    
    
    
    return make_response(json.dumps("Hooray!"), 200)
    
@app.route("/admin-daily", methods=["GET", "POST"])
@admin_required
def admin_daily():
    if request.method == "POST":
        pass
            
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

@app.route("/admin-writedailyroute", methods=["POST"])
@admin_required
def admin_writeDailyRoute():
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
            "INSERT INTO dailyroutes (route_id, routejson, routedate) VALUES ((SELECT IFNULL(MAX(route_id), 0) + 1 FROM dailyroutes), ?, DATE('now'))",
            (json.dumps(req),)
        )
    else:
        dates = [obj[0] for obj in raw]
        selectedDate = find_missing_consecutive_date(dates)
        query_database(
            os.path.join(DIRNAME, "database/mhdle_private.db"),
            "INSERT INTO dailyroutes (route_id, routejson, routedate) VALUES ((SELECT IFNULL(MAX(route_id), 0) + 1 FROM dailyroutes), ?, ?)",
            (json.dumps(req), selectedDate)
        )
    
    raw = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "SELECT routejson, routedate, route_id FROM dailyroutes WHERE routedate >= DATE('now') ORDER BY routedate DESC",
        False
        )
    #print(raw)
    if len(raw) != 0:
        jsonobject = [{"routejson": json.loads(obj[0]), "routedate": obj[1], "route_id": obj[2]} for obj in raw]
    else:
        jsonobject = 0
    
    data = json.dumps(jsonobject, indent=4)
    print(data)
    
    return make_response(data, 200)

@app.route("/admin-deletedailyroute", methods=["POST"])
@admin_required
def admin_deleteDailyRoute():
    query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "DELETE FROM dailyroutes WHERE route_id = (SELECT route_id FROM dailyroutes WHERE routedate > DATE('now') ORDER BY routedate DESC LIMIT 1)",
        False
    ) # admins can only delete routes for upcoming days 
    
    raw = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "SELECT routejson, routedate, route_id FROM dailyroutes WHERE routedate >= DATE('now') ORDER BY routedate DESC",
        False
        )
    #print(raw)
    if len(raw) != 0:
        jsonobject = [{"routejson": json.loads(obj[0]), "routedate": obj[1], "route_id": obj[2]} for obj in raw]
    else:
        jsonobject = 0
    
    data = json.dumps(jsonobject, indent=4)
    print(data)
    return make_response(data, 200)

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
    print("success")
    return out

@app.route('/logDailyRoute', methods=["POST"])
def logDailyRoute():
    req = request.get_json()
    user_id = session.get("user_id")
    route_id = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "SELECT route_id FROM dailyroutes WHERE routedate = DATE('now')",
        False
    )[0][0]
    print('ayoooooo')
    print("///")
    print()
    if req["status"] == 0:
        req["numberOfGuesses"] = 7
    print(req)
    print(user_id)
    print(route_id)
    query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        "INSERT INTO dailyguesses (routedate, user_id, number_of_guesses) VALUES (?, ?, ?)",
        (datetime.date.today(), user_id, req["numberOfGuesses"])
    )
    return make_response("kek", 200)
    #return redirect("/")
    #return make_response(render_template("custommenu.html"))
    #return redirect("/viewDailyData")

@app.route('/logDailyProgress', methods=["POST"])
def logDailyProgress():
    req = request.get_json()
    user_id = session.get("user_id")
    query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """INSERT INTO solution_progress_table (routedate, user_id, route_order, labelone, labeltwo, labelthree)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (datetime.date.today(), user_id, req["currentrow"], req["guess0"], req["guess1"], req["guess2"])
    )
    return make_response("kek2", 200)

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

@app.route('/admin-picupload', methods=["GET", "POST"])
@admin_required
def uploadIcons():
    if request.method == "POST":
        if 'file' not in request.files:
            return 'No file has been uploaded'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'File uploaded successfully'
    else:
        return render_template("adminpicupload.html")

@app.route('/viewDailyData', methods=["GET", "POST"])
@login_required
def viewDailyData():
    rawData = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """SELECT dailyguesses.routedate, routejson, number_of_guesses
        FROM dailyguesses LEFT JOIN dailyroutes ON dailyguesses.routedate = dailyroutes.routedate
        WHERE user_id = ? ORDER BY dailyguesses.routedate DESC""",
        (session.get("user_id"),)
    )    
    data = [{"routedate": row[0], "linelist": json.loads(row[1])["linelist"], "number_of_guesses": row[2]} for row in rawData]
    
    global_average_guesses = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """SELECT avg(number_of_guesses)
        FROM dailyguesses ORDER BY routedate DESC""",
        False
    )[0][0]
    user_average_guesses = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """SELECT avg(number_of_guesses)
        FROM dailyguesses
        WHERE user_id = ? ORDER BY routedate DESC""",
        (session.get("user_id"),)
    )[0][0]
    datelist_raw = query_database(
        os.path.join(DIRNAME, "database/mhdle_private.db"),
        """SELECT routedate
        FROM dailyguesses
        WHERE user_id = ? AND number_of_guesses != 7 ORDER BY routedate DESC""",
        (session.get("user_id"),)
    )
    datelist = [line[0] for line in datelist_raw]
    #print(datelist)
    #print(datetime.date.today().strftime('%Y-%m-%d'))
    streaks = date_streaks(datelist, datetime.date.today().strftime('%Y-%m-%d'))
    
    # 0: total MHDle solves
    # 1: Global average guess #
    # 2: Player's average guess #
    # 3: Current streak
    # 4: Longest streak
    if global_average_guesses is None:
        global_average_guesses = 0
    if user_average_guesses is None:
        user_average_guesses = 0
    extra = (len(datelist_raw), round(global_average_guesses, 3), round(user_average_guesses, 3), streaks[1], streaks[0])
    
    print(extra)
    
    return render_template("viewdailydata.html", data = data, extra = extra)

with app.test_request_context():
    print("Hello")
    