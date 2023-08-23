from typing import Tuple, List
from route import Route
from routehelpers import *
import random

def main():
    #generateRoute(5, useGreyLines=True)
    myroute = generateRoute(length=3, useGreyLines=False, area=("staremesto", "ruzinov", "novemesto", "karlovaves", "petrzalka", "vrakuna",
        "podunajskebiskupice", "raca", "vajnory", "dubravka", "lamac", "devin", 
        "devinskanovaves", "zahorskabystrica", "jarovce", "rusovce", "cunovo"))
    #generateRoute(8,useGreyLines=True)
    print("---------------------------")
    for i in range(40):
        print()
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
        # initialize list of lines and stops, which will make up the route
        print(f"Starting standardGeneration of length {length}.")
        newroute = Route(length, area, useGreyLines, useHardMode, targetStop)
        return standardGeneration(1, newroute)
        if returnroute is None:
            return None
        (linelist, stoplist, passedstops) = returntuple
        print("---------------------------")
        for i in range(40):
            print()
        print("MHDLE:")
        print(f"Travel from {unpackStops(stoplist[0])} to {unpackStops(stoplist[-1])} using {len(linelist)} lines.")
        input()
        print(*linelist)
        print(unpackStops(stoplist))
        for lst in passedstops:
            print(unpackStops(lst))


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
                print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop)}")
                # if length > 1, then more lines and stops still have to be generated.
                if route.conditions.length > 1:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop)
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returnroute = standardGeneration(recDepth+1, route)

                    # if standardGeneration returns None, then no working route was found with the initial line and stop.
                    if returnroute is not None:
                        return returnroute

                    # if the call to standardGeneration of higher depth doesn't result in a linelist and stoplist that works, try another one.
                    route.data.linelist.pop()
                    route.data.stoplist.pop()
                # if length == 1, then only the initial line and stop have to be added, alongside the final stop
                else:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop)
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
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returnroute = standardGeneration(recDepth+1, route)
                    if returnroute is not None:
                        # surface from recursion
                        return returnroute
                    else:
                        route.data.linelist.pop()
                        route.data.stoplist.pop()
                        route.data.passedstoplist.pop()
                # if length == recDepth, then the last (core) line and stop has to be added, alongside a final stop
                else:
                    route.data.linelist.append(selectedLine)
                    route.data.stoplist.append(selectedStop["select"])
                    route.data.passedstoplist.append(selectedStop["passed"])
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
                print("    " * recDepth + f"Stop {unpackStops(selectedStop['select'])} does not work.")
            print("    " * recDepth + f"No stops work with line {selectedLine}, picking another line.")
        # if none of the lines work with any of the stops, return None.
        print("    " * recDepth + f"No lines work, returning None and going to depth {recDepth-1}")
        return None

    

if __name__ == "__main__":
    main()