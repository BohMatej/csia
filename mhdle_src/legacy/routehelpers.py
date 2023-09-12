import sqlite3
import os
from typing import Tuple, List, Dict

DIRNAME = os.path.dirname(__file__)


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

def packStopsFromAlias(stoplist):
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