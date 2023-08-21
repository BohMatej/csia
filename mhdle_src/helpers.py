import sqlite3
import os
import random
from typing import Tuple, List

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

def generateFirstLines(area: Tuple[str, ...], useGreyLines: bool) -> List[str]:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()

    area = list(unpackAreaTuple(area))
    possibleAreaLines = cur.execute("""SELECT DISTINCT line_label FROM services WHERE stop_id IN 
                                (SELECT stop_id FROM stops WHERE district IN (%s))""" % ','.join('?'*len(area)), area).fetchall()
    if useGreyLines == True:
        lines = possibleAreaLines
    else:
        possibleColorLines = cur.execute("SELECT label FROM lines WHERE color != '9e9e9e'").fetchall()
        lines = intersection(possibleAreaLines, possibleColorLines)

    out = []
    for t in lines:
        for item in t:
            out.append(item)
    
    cur.close()
    conn.close()
    return out

def generateFirstStops(area: Tuple[str, ...], useGreyLines: bool, linelist: List[str]) -> List[int]:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()

    stops = 0

    cur.close()
    conn.close()
    return stops

def transferIsPossible():
    pass

def finalStopIsPossible():
    pass

def generateCoreLines():
    pass

def generateCoreStops():
    pass

def generateFinalStops():
    pass

