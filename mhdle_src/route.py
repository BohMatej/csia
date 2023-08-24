import sqlite3
import os
from typing import Tuple, List, Dict
from routehelpers import *

DIRNAME = os.path.dirname(__file__)

class RouteConditions:
    def __init__(self, 
            length: int, 
            area: Tuple[str, ...], 
            useGreyLines: bool, 
            useHardMode: bool,
            targetStop: Tuple[int, bool],
            isWacky: bool) -> None:
        self.length = length
        self.area = area
        self.useGreyLines = useGreyLines
        self.useHardMode = useHardMode
        self.targetStop = targetStop
        self.isWacky = isWacky

class RouteData:
    def __init__(self) -> None:
        self.linelist = []
        self.excludedlinelist = []
        self.stoplist = []
        self.passedstoplist = []
        self.excludedstoplist = []
        self.walkingtransferlist = []
        self.walkingtransferlist.append(None)
        self.interlinedlist = []

class Route:
    def __init__(self, 
            length: int, 
            area: Tuple[str, ...], 
            useGreyLines: bool, 
            useHardMode: bool,
            targetStop: Tuple[int, bool],
            isWacky: bool) -> None:
        self.conditions = RouteConditions(length, area, useGreyLines, useHardMode, targetStop, isWacky)
        self.data = RouteData()

    def generateFirstLines(self) -> List[str]:
        conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
        cur = conn.cursor()

        area = list(unpackAreaTuple(self.conditions.area))
        possibleAreaLines = cur.execute("""SELECT DISTINCT line_label FROM services WHERE stop_id IN 
                                    (SELECT stop_id FROM stops WHERE district IN (%s))""" % ','.join('?'*len(area)), area).fetchall()
        if self.conditions.useGreyLines == True:
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

    def generateFirstStops(self, selectedLine: str) -> Dict:
        conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
        cur = conn.cursor()
        params = []
        params.append(selectedLine)
        params.extend(list(unpackAreaTuple(self.conditions.area)))
        
        stopsRaw = cur.execute("""SELECT stop_id FROM services WHERE line_label = ? AND stop_id IN
                            (SELECT stop_id FROM stops WHERE district IN (%s)) 
                            ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(self.conditions.area)), params).fetchall()
        stops = []
        for t in stopsRaw:
            for item in t:
                stops.append(item)

        excludedlines = []
        for stop in stops:
            excludedLines_LoT = cur.execute("""SELECT DISTINCT line_label FROM services WHERE line_label != ? AND stop_id = ?""", (selectedLine, stop)).fetchall()
            excludedlines_L = []
            for t in excludedLines_LoT:
                for item in t:
                    excludedlines_L.append(item)
            excludedlines.append(excludedlines_L)

        out = []
        for i in range(len(stops)):
            out.append({"select": stops[i], "excluded": excludedlines[i]})

        cur.close()
        conn.close()
        return out

    def generateCoreLines(self) -> List[str]:
        conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
        cur = conn.cursor()
        
        # get information about which subservices of the current line run on the current stop, and their order
        params1 = []
        params1.append(self.data.stoplist[-1])
        params1.append(self.data.linelist[-1])
        currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()
        #print(currentStopServiceData)

        # get information about all stops on current line inside of the allowed area
        params2 = []
        params2.append(self.data.linelist[-1])
        params2.extend(list(unpackAreaTuple(self.conditions.area)))
        stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                                WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                                ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(self.conditions.area)), params2).fetchall()
        
        # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
        flat_passedstops = [item for sublist in self.data.passedstoplist for item in sublist]
        subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
        acceptableStops = []
        for service in currentStopServiceData:
            for stop in stopsOnCurrentLine:
                if stop[0] == service[0] and stop[1] > service[1]:
                    if stop[2] in flat_passedstops or stop[2] in self.data.stoplist:
                        subserviceBreakpoint = stop[1]
                    elif stop[1] < subserviceBreakpoint:
                        acceptableStops.append(stop[2])
            subserviceBreakpoint = 9999

        # add stops which can be walk-transfered to 
        walk_transfer_pairs = []

        walk_transfer_pairs.extend(cur.execute("""SELECT stop_id, stoptwo_id FROM stops 
                                        JOIN nearstops ON stops.stop_id = nearstops.stopone_id
                                        WHERE stop_id IN (%s)""" % ','.join('?'*len(acceptableStops)), acceptableStops).fetchall())
        walk_transfer_pairs.extend(cur.execute("""SELECT stop_id, stopone_id FROM stops 
                                        JOIN nearstops ON stops.stop_id = nearstops.stoptwo_id
                                        WHERE stop_id IN (%s)""" % ','.join('?'*len(acceptableStops)), acceptableStops).fetchall())

        transferstops = []
        for t in walk_transfer_pairs:
            transferstops.append(t[1])

        params3 = []
        params3.extend(acceptableStops)
        params3.extend(transferstops)
        params3.extend(self.data.linelist)
        flat_excludedlinelist = [item for sublist in self.data.excludedlinelist for item in sublist]
        params3.extend(flat_excludedlinelist)

        # select all lines which can be transfered to, are of the correct color, and can be transfered onto within the zone allowed.
        if self.conditions.useGreyLines:
            transferableLines = cur.execute("""SELECT DISTINCT line_label FROM services WHERE stop_id IN (%s) 
                                            AND line_label NOT IN (%s)""" % (','.join('?'*(len(acceptableStops) + len(transferstops))), ','.join('?'*(len(self.data.linelist)+len(flat_excludedlinelist)))), params3).fetchall()
        else: 
            transferableLines = cur.execute("""SELECT DISTINCT line_label FROM services INNER JOIN lines ON services.line_label = lines.label
                                            WHERE stop_id IN (%s) AND line_label NOT IN (%s) 
                                            AND color != '9e9e9e'""" % (','.join('?'*(len(acceptableStops) + len(transferstops))), ','.join('?'*(len(self.data.linelist)+len(flat_excludedlinelist)))), params3).fetchall()
        
        acceptableStops.extend(transferstops)
        out = []
        for t in transferableLines:
            for item in t:
                out.append(item)


        #lines = cur.execute("""SELECT line_label FROM services INNER JOIN stops ON services.stop_id = stops.stop_id
        #                    WHERE """)

        cur.close()
        conn.close()
        return out

    def generateCoreStops(self, selectedLine: str) -> Dict:
        conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
        cur = conn.cursor()

        # get information about which subservices of the current line run on the current stop, and their order
        params1 = []
        params1.append(self.data.stoplist[-1])
        params1.append(self.data.linelist[-1])
        currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()

        # get information about all stops on current line inside of the allowed area
        params2 = []
        params2.append(self.data.linelist[-1])
        params2.extend(list(unpackAreaTuple(self.conditions.area)))
        stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                                WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                                ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(self.conditions.area)), params2).fetchall()
        
        # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
        flat_passedstops = [item for sublist in self.data.passedstoplist for item in sublist]
        flat_excludedstoplist = [item for sublist in self.data.excludedstoplist for item in sublist]
        subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
        acceptableStops = []

        for service in currentStopServiceData:
            for stop in stopsOnCurrentLine:
                if stop[0] == service[0] and stop[1] > service[1]:
                    if stop[2] in flat_passedstops or stop[2] in self.data.stoplist:
                        subserviceBreakpoint = stop[1]
                    elif stop[1] < subserviceBreakpoint and stop[2] not in flat_excludedstoplist:
                        acceptableStops.append(stop[2])
            subserviceBreakpoint = 9999

        # select stops onto which direct transfer is possible
        params3 = [self.data.linelist[-1]]
        params3.extend(acceptableStops)
        params3.append(selectedLine)
        directTransferStopsRaw = cur.execute("""SELECT DISTINCT subservice, order_in_subservice, stop_id FROM services WHERE line_label = ? 
                                            AND stop_id IN (%s) AND stop_id IN 
                                            (SELECT stop_id FROM services WHERE line_label = ?)""" % ','.join('?'*len(acceptableStops)), params3).fetchall()
        
        # select stops onto which walking transfer is possible

        walkingTransferStopsRaw = cur.execute("""SELECT DISTINCT current.subservice, current.order_in_subservice, current.stop_id, transfered.stop_id, walktime
                                            FROM services AS current 
                                            JOIN nearstops ON nearstops.stopone_id = current.stop_id JOIN services AS transfered ON nearstops.stoptwo_id = transfered.stop_id
                                            WHERE current.line_label = ?
                                            AND current.stop_id IN (%s) 
                                            AND transfered.stop_id IN (SELECT stop_id FROM services WHERE line_label = ?)
                                            """ % ','.join('?'*len(acceptableStops)), params3).fetchall()
        walkingTransferStopsRaw.extend(cur.execute("""SELECT DISTINCT current.subservice, current.order_in_subservice, current.stop_id, transfered.stop_id, walktime
                                            FROM services AS current 
                                            JOIN nearstops ON nearstops.stoptwo_id = current.stop_id JOIN services AS transfered ON nearstops.stopone_id = transfered.stop_id
                                            WHERE current.line_label = ?
                                            AND current.stop_id IN (%s) 
                                            AND transfered.stop_id IN (SELECT stop_id FROM services WHERE line_label = ?)
                                            """ % ','.join('?'*len(acceptableStops)), params3).fetchall())
        for tr in walkingTransferStopsRaw:
            print(f"{tr[0]}, {tr[1]}, {unpackStops(tr[2])}, {unpackStops(tr[3])}, {tr[4]}")

        
        # some ugly code to determine which stops are being covered by the trip and which lines will be inaccesible for future generation
        possibleStops = []
        skippedStops = []
        excludedStops = []
        exlcudedLines = []
        transfers = []
        interlinedServices = []

        # first, sort out the direct transfers
        for service in currentStopServiceData:
            for rawstop in directTransferStopsRaw:
                if rawstop[0] == service[0] and rawstop[1] > service[1]:
                    transfers.append(None)
                    possibleStops.append(rawstop[2])
                    temp = cur.execute("""SELECT stop_id FROM services 
                                    WHERE line_label = ? 
                                    AND subservice = ?
                                    AND order_in_subservice > ?
                                    AND order_in_subservice < ?""",
                                    (self.data.linelist[-1], rawstop[0], service[1], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    skippedStops.append(out)
                    temp = cur.execute("""SELECT stop_id FROM services
                                    WHERE line_label = ?
                                    AND subservice = ?
                                    AND order_in_subservice > ?""",
                                    (self.data.linelist[-1], rawstop[0], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    excludedStops.append(out)
                    temp = cur.execute("""SELECT line_label FROM services
                                    WHERE stop_id = ?
                                    AND line_label != ?""",
                                    (rawstop[2], self.data.linelist[-1]))
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    exlcudedLines.append(out)

                    traveledstops = []
                    traveledstops.append(self.data.stoplist[-1])
                    traveledstops.extend(skippedStops[-1])
                    traveledstops.append(rawstop[2])
                    #print(self.data.stoplist[-1])
                    linestuples = cur.execute("""SELECT line_label, subservice, order_in_subservice 
                                              FROM services WHERE stop_id = ? AND line_label != ?""", (self.data.stoplist[-1], self.data.linelist[-1])).fetchall()
                    
                    out = set()
                    for linetuple in linestuples:
                        tll = linetuple[0]
                        tss = linetuple[1]
                        to = linetuple[2]
                        success = True
                        for traveledstop in traveledstops:
                            result = cur.execute("""SELECT services_id FROM services WHERE line_label = ? 
                                                 AND stop_id = ? AND subservice = ? AND order_in_subservice = ?""", (tll, traveledstop, tss, to)).fetchone()
                            to += 1
                            if result is None:
                                success = False
                                break
                        if success == True:
                            out.add(tll)
                    interlinedServices.append(out)
                    
        # now sort out the walking transfers
        for service in currentStopServiceData:
            for rawstop in walkingTransferStopsRaw:
                if rawstop[0] == service[0] and rawstop[1] > service[1]:
                    transfers.append((rawstop[2], rawstop[4]))
                    possibleStops.append(rawstop[3])
                    temp = cur.execute("""SELECT stop_id FROM services 
                                    WHERE line_label = ? 
                                    AND subservice = ?
                                    AND order_in_subservice > ?
                                    AND order_in_subservice < ?""",
                                    (self.data.linelist[-1], rawstop[0], service[1], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    skippedStops.append(out)
                    temp = cur.execute("""SELECT stop_id FROM services
                                    WHERE line_label = ?
                                    AND subservice = ?
                                    AND order_in_subservice >= ?""",
                                    (self.data.linelist[-1], rawstop[0], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    excludedStops.append(out)
                    temp = cur.execute("""SELECT line_label FROM services
                                    WHERE stop_id IN (?, ?)
                                    AND line_label != ?""",
                                    (rawstop[2], rawstop[3], self.data.linelist[-1]))
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    exlcudedLines.append(out)

                    traveledstops = []
                    traveledstops.append(self.data.stoplist[-1])
                    traveledstops.extend(skippedStops[-1])
                    traveledstops.append(rawstop[2])
                    linestuples = cur.execute("""SELECT line_label, subservice, order_in_subservice 
                                              FROM services WHERE stop_id = ? AND line_label != ?""", (self.data.stoplist[-1], self.data.linelist[-1])).fetchall()
                    
                    out = set()
                    for linetuple in linestuples:
                        tll = linetuple[0]
                        tss = linetuple[1]
                        to = linetuple[2]
                        success = True
                        for traveledstop in traveledstops:
                            result = cur.execute("""SELECT services_id FROM services WHERE line_label = ? 
                                                 AND stop_id = ? AND subservice = ? AND order_in_subservice = ?""", (tll, traveledstop, tss, to)).fetchone()
                            to += 1
                            if result is None:
                                success = False
                                break
                        if success == True:
                            out.add(tll)
                    interlinedServices.append(out)

        out = []
        for i in range(len(possibleStops)):
            out.append({"select": possibleStops[i], "passed": skippedStops[i], "s_excluded": excludedStops[i], "l_excluded": exlcudedLines[i], "walking": transfers[i], "interlined": interlinedServices[i]})
        

        cur.close()
        conn.close()
        return out

    def generateFinalStops(self) -> Dict:
        conn = sqlite3.connect(os.path.join(DIRNAME, "../database/mhdle.db"))
        cur = conn.cursor()
        

        # get information about which subservices of the current line run on the current stop, and their order
        params1 = []
        params1.append(self.data.stoplist[-1])
        params1.append(self.data.linelist[-1])
        currentStopServiceData = cur.execute("SELECT subservice, order_in_subservice FROM services WHERE stop_id = ? AND line_label = ?", params1).fetchall()

        # get information about all stops on current line inside of the allowed area
        params2 = []
        params2.append(self.data.linelist[-1])
        params2.extend(list(unpackAreaTuple(self.conditions.area)))
        stopsOnCurrentLine = cur.execute("""SELECT subservice, order_in_subservice, stop_id FROM services
                                WHERE line_label = ? AND services.stop_id IN (SELECT stop_id FROM stops WHERE district IN (%s))
                                ORDER BY subservice ASC, order_in_subservice ASC""" % ','.join('?'*len(self.conditions.area)), params2).fetchall()
        
        # restrict stops on current line according to subservices, and not allowing to travel to/beyond a stop that the route has already been at
        flat_passedstops = [item for sublist in self.data.passedstoplist for item in sublist]
        subserviceBreakpoint = 9999 # lol, just need it to be a big number such that no order_in_subservice can reach it
        acceptableStops = []

        for service in currentStopServiceData:
            for stop in stopsOnCurrentLine:
                if stop[0] == service[0] and stop[1] > service[1]:
                    if stop[2] in flat_passedstops or stop[2] in self.data.stoplist:
                        subserviceBreakpoint = stop[1]
                    elif stop[1] < subserviceBreakpoint:
                        acceptableStops.append(stop[2])
            subserviceBreakpoint = 9999

        # select stops onto which transfer is possible
        params3 = [self.data.linelist[-1]]
        params3.extend(acceptableStops)

        kindaPossibleStopsRaw = cur.execute("""SELECT DISTINCT subservice, order_in_subservice, stop_id FROM services WHERE line_label = ? 
                                            AND stop_id IN (%s)""" % ','.join('?'*len(acceptableStops)), params3).fetchall()
        
        # some ugly code to determine which stops are being covered by the trip and will be inaccesible for future generation
        possibleStops = []
        skippedStops = []
        excludedStops = []
        exlcudedLines = []
        interlinedServices = []
        for service in currentStopServiceData:
            for rawstop in kindaPossibleStopsRaw:
                if rawstop[0] == service[0] and rawstop[1] > service[1]:
                    possibleStops.append(rawstop[2])
                    temp = cur.execute("""SELECT stop_id FROM services 
                                    WHERE line_label = ? 
                                    AND subservice = ?
                                    AND order_in_subservice > ?
                                    AND order_in_subservice < ?""",
                                    (self.data.linelist[-1], rawstop[0], service[1], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    skippedStops.append(out)
                    temp = cur.execute("""SELECT stop_id FROM services
                                    WHERE line_label = ?
                                    AND subservice = ?
                                    AND order_in_subservice > ?""",
                                    (self.data.linelist[-1], rawstop[0], rawstop[1])).fetchall()
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    excludedStops.append(out)
                    temp = cur.execute("""SELECT line_label FROM services
                                    WHERE stop_id = ?
                                    AND line_label != ?""",
                                    (rawstop[2], self.data.linelist[-1]))
                    out = []
                    for t in temp:
                        for item in t:
                            out.append(item)
                    exlcudedLines.append(out)

                    traveledstops = []
                    traveledstops.append(self.data.stoplist[-1])
                    traveledstops.extend(skippedStops[-1])
                    traveledstops.append(rawstop[2])
                    #print(self.data.stoplist[-1])
                    linestuples = cur.execute("""SELECT line_label, subservice, order_in_subservice 
                                              FROM services WHERE stop_id = ? AND line_label != ?""", (self.data.stoplist[-1], self.data.linelist[-1])).fetchall()
                    
                    out = set()
                    for linetuple in linestuples:
                        tll = linetuple[0]
                        tss = linetuple[1]
                        to = linetuple[2]
                        success = True
                        for traveledstop in traveledstops:
                            result = cur.execute("""SELECT services_id FROM services WHERE line_label = ? 
                                                 AND stop_id = ? AND subservice = ? AND order_in_subservice = ?""", (tll, traveledstop, tss, to)).fetchone()
                            to += 1
                            if result is None:
                                success = False
                                break
                        if success == True:
                            out.add(tll)
                    interlinedServices.append(out)

        out = []
        for i in range(len(possibleStops)):
            #out.append((unpackStops(possibleStopsRaw[i][2]), unpackStops(skippedStops[i])))
            out.append({"select": possibleStops[i], "passed": skippedStops[i], "s_excluded": excludedStops[i], "l_excluded": exlcudedLines[i], "interlined": interlinedServices[i]})
        

        cur.close()
        conn.close()
        return out
    
    def printRoute(self):
        print("--------- Printing Route -------")
        print()
        print(f"Travel from {unpackStops(self.data.stoplist[0])} to {unpackStops(self.data.stoplist[-1])} using {len(self.data.linelist)} lines.")
        print("Answers: ", end="")
        print(*self.data.linelist)
        print("Walking transfers:")
        print(self.data.walkingtransferlist)
        print("Interlined services:")
        print(self.data.interlinedlist)
        print()
        for i in range(len(self.data.linelist)):
            if i == 0:
                print("Start by taking ", end="")
            elif i < len(self.data.linelist)-1:
                print("Transfer to ", end="")
            if i < len(self.data.linelist)-1:
                if self.data.walkingtransferlist[i+1] is None:
                    print(f"{self.data.linelist[i]} to travel from {unpackStops(self.data.stoplist[i])} to {unpackStops(self.data.stoplist[i+1])}.")
                else:
                    
                    print(f"{self.data.linelist[i]} to travel from {unpackStops(self.data.stoplist[i])} to {unpackStops(self.data.walkingtransferlist[i+1][0])}.")
                    print(f"Walk from {unpackStops(self.data.walkingtransferlist[i+1][0])} to {unpackStops(self.data.stoplist[i+1])}. This transfer will take around {self.data.walkingtransferlist[i+1][1]} minutes.")
            else:
                print(f"Finally, use {self.data.linelist[i]} to travel from {unpackStops(self.data.stoplist[i])} to {unpackStops(self.data.stoplist[i+1])}.")

