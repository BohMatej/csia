import sqlite3
import os

# get directory name
DIRNAME = os.path.dirname(__file__)

# set up connection and cursor
conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
cur = conn.cursor()

# execute script
stops = cur.execute("SELECT alias, truename FROM stops").fetchall()
print(stops)
print("Here!")
cur.executemany("INSERT INTO aliases (alias, truename) VALUES (?,?)", stops)
conn.commit()
input()
# close connection and cursor
cur.close()
conn.close()