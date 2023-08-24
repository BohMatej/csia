from typing import Tuple, List
from route import Route
from routehelpers import *
import random

EVERYWHERE = ("staremesto", "ruzinov", "novemesto", "karlovaves", "petrzalka", "vrakuna",
        "podunajskebiskupice", "raca", "vajnory", "dubravka", "lamac", "devin", 
        "devinskanovaves", "zahorskabystrica", "jarovce", "rusovce", "cunovo")

def main():
    myroute = generateRoute()
    # myroute = verifyRoute(("72", "3", "95"))
    print("---------------------------")
    # for i in range(40):
    #     print()
    if myroute is None:
        print("Route is impossible.")
        return
    print("MHDLE:")
    print(f"Travel from {unpackStops(myroute.data.stoplist[0])} to {unpackStops(myroute.data.stoplist[-1])} using {len(myroute.data.linelist)} lines.")
    input()
    print(*myroute.data.linelist)
    print(unpackStops(myroute.data.stoplist))
    print("passing through")
    for lst in myroute.data.passedstoplist:
        print(unpackStops(lst))
    

def generateRoute(
        length: int = 3, 
        area: Tuple[str, ...] = ("staremesto", "ruzinov", "novemesto", "karlovaves", "petrzalka"), 
        useGreyLines: bool = False, 
        useHardMode: bool = False,
        targetStop: Tuple[int, bool] = None
        ) -> Route:
    
    if targetStop == None and useHardMode == False:
        print(f"Starting standardGeneration of length {length}.")
        newroute = Route(length, area, useGreyLines, useHardMode, targetStop, False)
        return standardGeneration(1, newroute)

def verifyRoute(enteredLines: Tuple[str, ...]) -> Route:
    print(f"Starting verification of an entry with lines: {enteredLines}.")
    newroute = Route(len(enteredLines), EVERYWHERE, True, False, None, False)
    return standardVerification(1, newroute, enteredLines)


def standardGeneration(recDepth: int, route: Route) -> Route:

    print("    " * recDepth + f"Recursion depth: {recDepth}")
    # base case: where the first line and stop is generated
    if (recDepth == 1):

        # generate first line
        print("    " * recDepth + "Generating first lines")
        lines = route.generateFirstLines()
        random.shuffle(lines)

        for selectedLine in lines:
            print("    " * recDepth + f"Selected line: {selectedLine}")
            # generate first stop
            print("    " * recDepth + "Generating first stops")
            stops = route.generateFirstStops(selectedLine)
            random.shuffle(stops)
            

            for selectedStop in stops:
                print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop['select'])}")
                # if length > 1, then more lines and stops still have to be generated.
                if route.conditions.length > 1:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop["select"])
                    route.data.excludedlinelist.append(selectedStop["excluded"])
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returnroute = standardGeneration(recDepth+1, route)

                    # if standardGeneration returns None, then no working route was found with the initial line and stop.
                    if returnroute is not None:
                        return returnroute

                    # if the call to standardGeneration of higher depth doesn't result in a linelist and stoplist that works, try another one.
                    route.data.linelist.pop()
                    route.data.stoplist.pop()
                    route.data.excludedlinelist.pop()
                # if length == 1, then only the initial line and stop have to be added, alongside the final stop
                else:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop["select"])
                    route.data.excludedlinelist.append(selectedStop["excluded"])
                    print("    " * recDepth + "Generating final stop")
                    final_stops = route.generateFinalStops()
                    random.shuffle(final_stops)

                    for selectedFinalStop in final_stops:
                        print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                        route.data.stoplist.append(selectedFinalStop["select"])
                        route.data.passedstoplist.append(selectedFinalStop["passed"])
                        # do not recursivbely call, as this route is verified to be possible
                        return route
                    route.data.linelist.pop()
                    route.data.stoplist.pop()
                    route.data.excludedlinelist.pop()
        # if none of the lines work
        print("    " * recDepth + "Sorry, the conditions for the route you picked can't generate a route.")
        return None
    
    # core (or final) case
    else:
        # generate core line
        print("    " * recDepth + "Generating core lines")
        lines = route.generateCoreLines()
        random.shuffle(lines)

        for selectedLine in lines:
            print("    " * recDepth + f"Selected line: {selectedLine}")
            # generate core stops 
            # returns a dict because I'm a dumbass; "select" key represents the selected stop, and "passed" key represents a list of stops which were passed when traveling
            print("    " * recDepth + "Generating core stops")
            stops = route.generateCoreStops(selectedLine)
            random.shuffle(stops)
            #print(stops)
            #print(type(stops))
            #print(type(stops[0]["select"]))

            for selectedStop in stops:
                print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop['select'])}")
                # if length > recDepth, then more lines and stops still have to be generated.
                if route.conditions.length > recDepth:
                    #if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop["select"])
                    route.data.passedstoplist.append(selectedStop["passed"])
                    route.data.excludedlinelist.append(selectedStop["l_excluded"])
                    route.data.excludedstoplist.append(selectedStop["s_excluded"])
                    route.data.walkingtransferlist.append(selectedStop["walking"])
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returnroute = standardGeneration(recDepth+1, route)
                    if returnroute is not None:
                        # surface from recursion
                        return returnroute
                    else:
                        route.data.linelist.pop()
                        route.data.stoplist.pop()
                        route.data.passedstoplist.pop()
                        route.data.excludedlinelist.pop()
                        route.data.excludedstoplist.pop()
                        route.data.walkingtransferlist.pop()
                # if length == recDepth, then the last (core) line and stop has to be added, alongside a final stop
                else:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop["select"])
                    route.data.passedstoplist.append(selectedStop["passed"])
                    route.data.excludedlinelist.append(selectedStop["l_excluded"])
                    route.data.excludedstoplist.append(selectedStop["s_excluded"])
                    route.data.walkingtransferlist.append(selectedStop["walking"])
                    print("    " * recDepth + "Generating final stops")
                    final_stops = route.generateFinalStops()
                    random.shuffle(final_stops)

                    for selectedFinalStop in final_stops:
                        print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                        route.data.stoplist.append(selectedFinalStop["select"])
                        route.data.passedstoplist.append(selectedFinalStop["passed"])
                        route.data.excludedstoplist.append(selectedFinalStop["s_excluded"])
                        # do not recursivbely call, as this route is verified to be possible
                        return route
                    route.data.linelist.pop()
                    route.data.stoplist.pop()
                    route.data.passedstoplist.pop()
                    route.data.excludedlinelist.pop()
                    route.data.excludedstoplist.pop()
                    route.data.walkingtransferlist.pop()
                print("    " * recDepth + f"Stop {unpackStops(selectedStop['select'])} does not work.")
            print("    " * recDepth + f"No stops work with line {selectedLine}, picking another line.")
        # if none of the lines work with any of the stops, return None.
        print("    " * recDepth + f"No lines work, returning None and going to depth {recDepth-1}")
        return None

def standardVerification(recDepth: int, route: Route, enteredLines: Tuple[str, ...]) -> Route:
    print("    " * recDepth + f"Recursion depth: {recDepth}")
    # base case: where the first line and stop is generated
    if (recDepth == 1):

        # select first line
        selectedLine = enteredLines[recDepth-1]
        print("    " * recDepth + f"Selected line: {selectedLine}")
        # generate first stop
        print("    " * recDepth + "Generating first stops")
        stops = route.generateFirstStops(selectedLine)
        random.shuffle(stops)
        
        for selectedStop in stops:
            print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop['select'])}")
            # if length > 1, then more lines and stops still have to be generated.
            if route.conditions.length > 1:
                route.data.linelist.append(selectedLine)
                route.data.stoplist.append(selectedStop['select'])
                # recursively call standardVerification at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                returnroute = standardVerification(recDepth+1, route, enteredLines)

                # if standardVerification returns None, then no working route was found with the initial line and stop.
                if returnroute is not None:
                    return returnroute

                # if the call to standardVerification of higher depth doesn't result in a linelist and stoplist that works, try another one.
                route.data.linelist.pop()
                route.data.stoplist.pop()
            # if length == 1, then only the initial line and stop have to be added, alongside the final stop
            else:
                route.data.linelist.append(selectedLine)
                route.data.stoplist.append(selectedStop['select'])
                print("    " * recDepth + "Generating final stop")
                final_stops = route.generateFinalStops()
                random.shuffle(final_stops)

                for selectedFinalStop in final_stops:
                    print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                    route.data.stoplist.append(selectedFinalStop["select"])
                    route.data.passedstoplist.append(selectedFinalStop["passed"])
                    # do not recursivbely call, as this route is verified to be possible
                    return route
                route.data.linelist.pop()
                route.data.stoplist.pop()
        # if none of the lines work
        print("    " * recDepth + "Sorry, the conditions for the route you picked can't generate a route.")
        return None
    
    # core (or final) case
    else:
        # select core line
        selectedLine = enteredLines[recDepth-1]
        print("    " * recDepth + f"Selected line: {selectedLine}")
        # generate core stops 
        # returns a dict because I'm a dumbass; "select" key represents the selected stop, and "passed" key represents a list of stops which were passed when traveling
        print("    " * recDepth + "Generating core stops")
        stops = route.generateCoreStops(selectedLine)
        random.shuffle(stops)

        for selectedStop in stops:
            print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop['select'])}")
            # if length > recDepth, then more lines and stops still have to be generated.
            if route.conditions.length > recDepth:
                #if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                route.data.linelist.append(selectedLine)
                route.data.stoplist.append(selectedStop["select"])
                route.data.passedstoplist.append(selectedStop["passed"])
                route.data.walkingtransferlist.append(selectedStop["walking"])
                # recursively call standardVerification at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                returnroute = standardVerification(recDepth+1, route, enteredLines)
                if returnroute is not None:
                    # surface from recursion
                    return returnroute
                else:
                    route.data.linelist.pop()
                    route.data.stoplist.pop()
                    route.data.passedstoplist.pop()
                    route.data.walkingtransferlist.pop()
            # if length == recDepth, then the last (core) line and stop has to be added, alongside a final stop
            else:
                route.data.linelist.append(selectedLine)
                route.data.stoplist.append(selectedStop["select"])
                route.data.passedstoplist.append(selectedStop["passed"])
                route.data.walkingtransferlist.append(selectedStop["walking"])
                print("    " * recDepth + "Generating final stops")
                final_stops = route.generateFinalStops()
                random.shuffle(final_stops)

                for selectedFinalStop in final_stops:
                    print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                    route.data.stoplist.append(selectedFinalStop["select"])
                    route.data.passedstoplist.append(selectedFinalStop["passed"])
                    # do not recursivbely call, as this route is verified to be possible
                    return route
                route.data.linelist.pop()
                route.data.stoplist.pop()
                route.data.passedstoplist.pop()
                route.data.walkingtransferlist.pop()
            print("    " * recDepth + f"Stop {unpackStops(selectedStop['select'])} does not work.")
        # if none of the lines work with any of the stops, return None.
        print("    " * recDepth + f"No lines work, returning None and going to depth {recDepth-1}")
        return None

if __name__ == "__main__":
    main()