import sqlite3
import os
import random
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
        stopids.append(cur.execute("SELECT stop_id FROM stops WHERE alias = ?", (stop,)).fetchone())

    out = []
    for t in stopids:
        for item in t:
            out.append(item)

    cur.close()
    conn.close()
    return out

def generateFirstLines(area: Tuple[str, ...], useGreyLines: bool) -> List[str]:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()

    print("Generating first line")

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

def generateFirstStops(area: Tuple[str, ...], selectedLine: str) -> List[int]:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    print("Generating first stops")
    params = []
    params.append(selectedLine)
    params.extend(list(unpackAreaTuple(area)))
    
    stops = cur.execute("""SELECT stop_id FROM services WHERE line_label = ? AND stop_id IN
                        (SELECT stop_id FROM stops WHERE district IN (%s)) ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(area)), params).fetchall()

    out = []
    for t in stops:
        for item in t:
            out.append(item)

    cur.close()
    conn.close()
    return out

def generateCoreLines(area: Tuple[str, ...], useGreyLines: bool, linelist: List[str], stoplist: List[int], passedstops: List[List[int]]) -> List[str]:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    print("Generating core lines")
    
    # get information about which subservices of the current line run on the current stop, and their order
    params1 = []
    params1.append(stoplist[-1])
    params1.append(linelist[-1])
    currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()
    #print(currentStopServiceData)

    # get information about all stops on current line inside of the allowed area
    params2 = []
    params2.append(linelist[-1])
    params2.extend(list(unpackAreaTuple(area)))
    stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                            WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                            ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(area)), params2).fetchall()
    
    # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
    flat_passedstops = [item for sublist in passedstops for item in sublist]
    subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
    acceptableStops = []
    for service in currentStopServiceData:
        for stop in stopsOnCurrentLine:
            if stop[0] == service[0] and stop[1] > service[1]:
                if stop[2] in flat_passedstops or stop[2] in stoplist:
                    subserviceBreakpoint = stop[1]
                elif stop[1] < subserviceBreakpoint:
                    acceptableStops.append(stop[2])
        subserviceBreakpoint = 9999
    
    #firstCall = cur.execute("""SELECT line_label, subservice, order_in_subservice, truename FROM services INNER JOIN stops ON services.stop_id = stops.stop_id
    #                        WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
    #                        ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(area)), params).fetchall()

    #for stops in stopsOnCurrentLine:
    #    print((stops[0], stops[1], unpackStops(stops[2]),))
    #for stop in acceptableStops:
    #    print(unpackStops(stop))

    params3 = []
    params3.extend(acceptableStops)
    params3.extend(linelist)

    # select all lines which can be transfered to, are of the correct color, and can be transfered onto within the zone allowed.
    if useGreyLines:
        transferableLines = cur.execute("""SELECT DISTINCT line_label FROM services WHERE stop_id IN (%s) 
                                        AND line_label NOT IN (%s)""" % (','.join('?'*len(acceptableStops)), ','.join('?'*len(linelist))), params3).fetchall()
    else: 
        transferableLines = cur.execute("""SELECT DISTINCT line_label FROM services INNER JOIN lines ON services.line_label = lines.label
                                        WHERE stop_id IN (%s) AND line_label NOT IN (%s) 
                                        AND color != '9e9e9e'""" % (','.join('?'*len(acceptableStops)), ','.join('?'*len(linelist))), params3).fetchall()

    out = []
    for t in transferableLines:
        for item in t:
            out.append(item)

    #print(out)

    #lines = cur.execute("""SELECT line_label FROM services INNER JOIN stops ON services.stop_id = stops.stop_id
    #                    WHERE """)

    cur.close()
    conn.close()
    return out

def generateCoreStops(area: Tuple[str, ...], linelist: List[str], stoplist: List[int], passedstops: List[List[int]], selectedLine: str) -> Dict:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    print("Generating core stops")

    # get information about which subservices of the current line run on the current stop, and their order
    params1 = []
    params1.append(stoplist[-1])
    params1.append(linelist[-1])
    currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()

    # get information about all stops on current line inside of the allowed area
    params2 = []
    params2.append(linelist[-1])
    params2.extend(list(unpackAreaTuple(area)))
    stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                            WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                            ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(area)), params2).fetchall()
    
    # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
    flat_passedstops = [item for sublist in passedstops for item in sublist]
    subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
    acceptableStops = []

    for service in currentStopServiceData:
        for stop in stopsOnCurrentLine:
            if stop[0] == service[0] and stop[1] > service[1]:
                if stop[2] in flat_passedstops or stop[2] in stoplist:
                    subserviceBreakpoint = stop[1]
                elif stop[1] < subserviceBreakpoint:
                    acceptableStops.append(stop[2])
        subserviceBreakpoint = 9999

    # select stops onto which transfer is possible
    params3 = [linelist[-1]]
    params3.extend(acceptableStops)
    params3.append(selectedLine)

    kindaPossibleStopsRaw = cur.execute("""SELECT DISTINCT subservice, order_in_subservice, stop_id FROM services WHERE line_label = ? 
                                        AND stop_id IN (%s) AND stop_id IN 
                                        (SELECT stop_id FROM services WHERE line_label = ?)""" % ','.join('?'*len(acceptableStops)), params3).fetchall()
    
    # some ugly code to determine which stops are being covered by the trip and will be inaccesible for future generation
    possibleStopsRaw = []
    skippedStops = []
    for service in currentStopServiceData:
        for rawstop in kindaPossibleStopsRaw:
            if rawstop[0] == service[0] and rawstop[1] > service[1]:
                possibleStopsRaw.append(rawstop)
                temp = cur.execute("""SELECT stop_id FROM services 
                                   WHERE line_label = ? 
                                   AND subservice = ?
                                   AND order_in_subservice > ?
                                   AND order_in_subservice < ?""",
                                   (linelist[-1], rawstop[0], service[1], rawstop[1])).fetchall()
                out = []
                for t in temp:
                    for item in t:
                        out.append(item)
                skippedStops.append(out)

    out = []
    for i in range(len(possibleStopsRaw)):
        #out.append((unpackStops(possibleStopsRaw[i][2]), unpackStops(skippedStops[i])))
        out.append({"select": possibleStopsRaw[i][2], "passed": skippedStops[i]})
    

    cur.close()
    conn.close()
    return out

def generateFinalStops(area: Tuple[str, ...], linelist: List[str], stoplist: List[int], passedstops: List[List[int]]) -> Dict:
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()
    print("Generating final stop")

    # get information about which subservices of the current line run on the current stop, and their order
    params1 = []
    params1.append(stoplist[-1])
    params1.append(linelist[-1])
    currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()

    # get information about all stops on current line inside of the allowed area
    params2 = []
    params2.append(linelist[-1])
    params2.extend(list(unpackAreaTuple(area)))
    stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                            WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                            ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(area)), params2).fetchall()
    
    # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
    flat_passedstops = [item for sublist in passedstops for item in sublist]
    subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
    acceptableStops = []

    for service in currentStopServiceData:
        for stop in stopsOnCurrentLine:
            if stop[0] == service[0] and stop[1] > service[1]:
                if stop[2] in flat_passedstops or stop[2] in stoplist:
                    subserviceBreakpoint = stop[1]
                elif stop[1] < subserviceBreakpoint:
                    acceptableStops.append(stop[2])
        subserviceBreakpoint = 9999

    # select stops onto which transfer is possible
    params3 = [linelist[-1]]
    params3.extend(acceptableStops)

    kindaPossibleStopsRaw = cur.execute("""SELECT DISTINCT subservice, order_in_subservice, stop_id FROM services WHERE line_label = ? 
                                        AND stop_id IN (%s)""" % ','.join('?'*len(acceptableStops)), params3).fetchall()
    
    # some ugly code to determine which stops are being covered by the trip and will be inaccesible for future generation
    possibleStopsRaw = []
    skippedStops = []
    for service in currentStopServiceData:
        for rawstop in kindaPossibleStopsRaw:
            if rawstop[0] == service[0] and rawstop[1] > service[1]:
                possibleStopsRaw.append(rawstop)
                temp = cur.execute("""SELECT stop_id FROM services 
                                   WHERE line_label = ? 
                                   AND subservice = ?
                                   AND order_in_subservice > ?
                                   AND order_in_subservice < ?""",
                                   (linelist[-1], rawstop[0], service[1], rawstop[1])).fetchall()
                out = []
                for t in temp:
                    for item in t:
                        out.append(item)
                skippedStops.append(out)

    out = []
    for i in range(len(possibleStopsRaw)):
        #out.append((unpackStops(possibleStopsRaw[i][2]), unpackStops(skippedStops[i])))
        out.append({"select": possibleStopsRaw[i][2], "passed": skippedStops[i]})
    

    cur.close()
    conn.close()
    return out

def transferIsPossible(area: Tuple[str, ...], linelist: List[str], stoplist: List[int], selectedLine: str, selectedStop: int):
    conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
    cur = conn.cursor()

    status = True

    cur.close()
    conn.close()
    return status
