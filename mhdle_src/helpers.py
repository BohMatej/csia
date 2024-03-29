import sqlite3
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, date, timedelta
import os
from typing import Tuple, List, Dict

DIRNAME = os.path.dirname(__file__)

# WSGI helpers

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
            ''' this situation should never happen realistically, 
                as buttons with links to these routes don't show for
                non-admins. However, it acts as a failsafe on the backend,
                as a user with malicious intent that know the link to an
                admin-only route could otherwise access it.'''
        return f(*args, **kwargs)
    return decorated_function

def daily_not_beaten_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        datelistlmao = query_database(
            os.path.join(DIRNAME, "../database/mhdle_private.db"),
            """SELECT routedate
            FROM dailyguesses
            WHERE user_id = ? AND routedate = ?""",
            (session.get("user_id"), date.today())
        )
        if len(datelistlmao) != 0:
            return "You have already completed today's MHDle."
        return f(*args, **kwargs)
    return decorated_function



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


def date_streaks(date_list, latest_date):
    if not date_list or not latest_date:
        return (0, 0)
    
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in date_list]
    latest_date = datetime.strptime(latest_date, "%Y-%m-%d")
    date_objects.sort()

    current_streak = 1
    longest_streak = 1
    streak_including_previous_day = 0

    if len(date_objects) > 1:
        for i in range(1, len(date_objects)):
            if (date_objects[i] - date_objects[i - 1]).days == 1:
                current_streak += 1
            else:
                current_streak = 1

            longest_streak = max(longest_streak, current_streak)

            if date_objects[i] <= latest_date:
                streak_including_previous_day = current_streak  

        if (latest_date - date_objects[len(date_objects)-1]).days > 1:
            streak_including_previous_day = 0
    elif len(date_objects) == 1:
        if (latest_date - date_objects[0]).days < 2: # only one day played, and it's either today od yesterday. Hence, keep 1 streak
            streak_including_previous_day = 1
    else:
        return (0, 0)
    return (longest_streak, streak_including_previous_day)

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