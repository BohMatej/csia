import sqlite3
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta

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