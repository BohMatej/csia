import sqlite3
import os

# get directory name
DIRNAME = os.path.dirname(__file__)

# set up connection and cursor
conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
cur = conn.cursor()

# load SQL script from file
with open(os.path.join(DIRNAME, "dbinit.sql")) as file:
    sql_script = file.read()

# execute script
cur.executescript(sql_script)

# close connection and cursor
cur.close()
conn.close()