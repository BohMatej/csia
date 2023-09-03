import os
import sys
sys.path.append("mhdle_src")
from flask import Flask, redirect, render_template, request, session, url_for, jsonify, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json
from routegeneration import generateRoute, verifyRoute
from routehelpers import unpackStops

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



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

@app.route('/login')
def login():
    return 'login'

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

with app.test_request_context():
    print("Hello")