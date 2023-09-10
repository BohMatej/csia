import sqlite3
from flask import redirect, render_template, session
from functools import wraps

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
        output_superraw = cur.execute(query, arguments)
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