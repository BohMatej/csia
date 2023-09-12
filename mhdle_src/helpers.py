import sqlite3
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta
import os
from typing import Tuple, List, Dict

DIRNAME = os.path.dirname(__file__)

# WSGI helpers

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session.get("user_id") != 1:
            return "Page is only accessible to the admin."
        return f(*args, **kwargs)
    return decorated_function

def query_database(dbpath: str, query: str, arguments, fetchtype = "all", executetype: str = "single"):
    # create connection and cursor
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    
    # execute query, returning a cursor object
    if executetype == "single":
        if arguments is False:
            output_superraw = cur.execute(query)
        else:
            output_superraw = cur.execute(query, arguments)
    else:
        if arguments is False:
            output_superraw = cur.executemany(query, arguments)
        else:
            output_superraw = cur.executemany(query, arguments)
    
    # fetch data from the cursor object
    if fetchtype == "all":
        output_raw = output_superraw.fetchall()
    elif fetchtype == "one":
        output_raw = output_superraw.fetchone()
    else:
        output_raw = output_superraw.fetchmany(fetchtype)
    
    conn.commit()
    cur.close()
    conn.close()
    return output_raw # because.

def find_missing_consecutive_date(date_list):
    if not date_list:
        return None

    date_list = sorted(date_list)
    start_date = datetime.strptime(date_list[0], "%Y-%m-%d")
    
    for date_str in date_list:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date == start_date:
            start_date += timedelta(days=1)
        else:
            return start_date.strftime("%Y-%m-%d")

    return (start_date).strftime("%Y-%m-%d")

# route helpers

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def unpackAreaTuple(area: Tuple[str, ...]) -> Tuple[str, ...]:
    dictionary = {
        "staremesto": "Staré Mesto",
        "ruzinov": "Ružinov",
        "novemesto": "Nové Mesto",
        "karlovaves": "Karlova Ves",
        "petrzalka": "Petržalka",
        "vrakuna": "Vrakuňa",
        "podunajskebiskupice": "Podunajské Biskupice",
        "raca": "Rača",
        "vajnory": "Vajnory",
        "dubravka": "Dúbravka",
        "lamac": "Lamač",
        "devin": "Devín",
        "devinskanovaves": "Devínska Nová Ves",
        "zahorskabystrica": "Záhorská Bystrica",
        "jarovce": "Jarovce",
        "rusovce": "Rusovce",
        "cunovo": "Čunovo"
    }
    newlist = []
    for item in area:
        newlist.append(dictionary[item])
    return tuple(newlist)

def unpackStops(stoplist):
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    if type(stoplist) in [list, tuple, set]:
        truenames = []
        for stop in stoplist:
            truenames.append(cur.execute("SELECT truename FROM stops WHERE stop_id = ?", (stop,)).fetchone())

        out = []
        for t in truenames:
            for item in t:
                out.append(item)
    elif type(stoplist) in [int, str]:
        out = cur.execute("SELECT truename FROM stops WHERE stop_id = ?", (stoplist,)).fetchone()[0]

    cur.close()
    conn.close()
    return out

def packStopsFromAlias(stoplist): # legacy: used for manual stop input
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    stopids = []
    for stop in stoplist:
        stopids.append(cur.execute("SELECT stop_id FROM stops WHERE truename = (SELECT truename FROM aliases WHERE alias = ?)", (stop,)).fetchone())

    out = []
    for t in stopids:
        for item in t:
            out.append(item)

    cur.close()
    conn.close()
    return out