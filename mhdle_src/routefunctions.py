from typing import Tuple, List
from helpers import *
import random

def main():
    #generateRoute(5, useGreyLines=True)
    generateRoute(length=3, useGreyLines=False, area=("staremesto", "ruzinov", "novemesto", "karlovaves", "petrzalka", "vrakuna",
        "podunajskebiskupice", "raca", "vajnory", "dubravka", "lamac", "devin", 
        "devinskanovaves", "zahorskabystrica", "jarovce", "rusovce", "cunovo"))
    #generateRoute(8,useGreyLines=True)

def generateRoute(
        length: int = 3, 
        area: Tuple[str, ...] = ("staremesto", "ruzinov", "novemesto", "karlovaves", "petrzalka"), 
        useGreyLines: bool = False, 
        useHardMode: bool = False,
        targetStop: Tuple[int, bool] = None
        ) -> Tuple[Tuple[str, ...], Tuple[int, ...]]:
    
    if targetStop == None and useHardMode == False:
        # initialize list of lines and stops, which will make up the route
        linelist = []
        stoplist = []
        passedstops = []
        #print(generateFirstLines(area, useGreyLines))
        #print(unpackStops(generateFirstStops(area, "29")))
        #print(generateCoreLines(area, useGreyLines, ["41"], packStopsFromAlias(["safranova"]), [packStopsFromAlias(["hrobonova", "budkova"])]))
        #print(generateCoreStops(area, ["41"], packStopsFromAlias(["safranova"]), [], '47'))
        
        print(f"Starting standardGeneration of length {length}.")
        returntuple = standardGeneration(1, length, area, useGreyLines, linelist, stoplist, passedstops)
        if returntuple is None:
            return
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


def standardGeneration(
        recDepth: int,
        length: int, 
        area: Tuple[str, ...], 
        useGreyLines: bool,
        linelist: List[str],
        stoplist: List[int],
        passedstops: List[int]
        ) -> Tuple[Tuple[str, ...], Tuple[int, ...], Tuple[List[int], ...]]:


    print("    " * recDepth + f"Recursion depth: {recDepth}")
    # base case: where the first line and stop is generated
    if (recDepth == 1):

        # generate first line
        print("    " * recDepth + "Generating first lines")
        lines = generateFirstLines(area, useGreyLines)
        random.shuffle(lines)

        for selectedLine in lines:
            print("    " * recDepth + f"Selected line: {selectedLine}")
            # generate first stop
            print("    " * recDepth + "Generating first stops")
            stops = generateFirstStops(area, selectedLine)
            random.shuffle(stops)
            

            for selectedStop in stops:
                print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop)}")
                # if length > 1, then more lines and stops still have to be generated.
                if length > 1:
                    #if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                    linelist.append(selectedLine)
                    stoplist.append(selectedStop)
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returntuple = standardGeneration(recDepth+1, length, area, useGreyLines, linelist, stoplist, passedstops)

                    # if standardGeneration returns None, then no working route was found with the initial line and stop.
                    if returntuple is not None:
                        (linelist, stoplist, passedstops) = returntuple
                        # recursion is now finished
                        return linelist, stoplist, passedstops

                    # if the call to standardGeneration of higher depth doesn't result in a linelist and stoplist that works, try another one.
                    linelist.pop()
                    stoplist.pop()
                # if length == 1, then only the initial line and stop have to be added, alongside the final stop
                else:
                    linelist.append(selectedLine)
                    stoplist.append(selectedStop)
                    print("    " * recDepth + "Generating final stop")
                    final_stops = generateFinalStops(area, linelist, stoplist, passedstops)
                    random.shuffle(final_stops)

                    for selectedFinalStop in final_stops:
                        print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                        stoplist.append(selectedFinalStop["select"])
                        passedstops.append(selectedFinalStop["passed"])
                        # do not recursivbely call, as this route is verified to be possible
                        return linelist, stoplist, passedstops
                    linelist.pop()
                    stoplist.pop()
        # if none of the lines work
        print("    " * recDepth + "Sorry, the conditions for the route you picked can't generate a route.")
        return None
    
    # core (or final) case
    else:
        # generate core line
        print("    " * recDepth + "Generating core lines")
        lines = generateCoreLines(area, useGreyLines, linelist, stoplist, passedstops)
        random.shuffle(lines)

        for selectedLine in lines:
            print("    " * recDepth + f"Selected line: {selectedLine}")
            # generate core stops 
            # returns a dict because I'm a dumbass; "select" key represents the selected stop, and "passed" key represents a list of stops which were passed when traveling
            print("    " * recDepth + "Generating core stops")
            stops = generateCoreStops(area, linelist, stoplist, passedstops, selectedLine)
            random.shuffle(stops)
            #print(stops)
            #print(type(stops))
            #print(type(stops[0]["select"]))

            for selectedStop in stops:
                print("    " * recDepth + f"Selected stop: {unpackStops(selectedStop['select'])}")
                # if length > recDepth, then more lines and stops still have to be generated.
                if length > recDepth:
                    #if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                    linelist.append(selectedLine)
                    stoplist.append(selectedStop["select"])
                    passedstops.append(selectedStop["passed"])
                    # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                    returntuple = standardGeneration(recDepth+1, length, area, useGreyLines, linelist, stoplist, passedstops)
                    if returntuple is not None:
                        # surface from recursion
                        (linelist, stoplist, passedstops) = returntuple
                        return linelist, stoplist, passedstops
                    else:
                        linelist.pop()
                        stoplist.pop()
                        passedstops.pop()
                # if length == recDepth, then the last (core) line and stop has to be added, alongside a final stop
                else:
                    linelist.append(selectedLine)
                    stoplist.append(selectedStop["select"])
                    passedstops.append(selectedStop["passed"])
                    print("    " * recDepth + "Generating final stops")
                    final_stops = generateFinalStops(area, linelist, stoplist, passedstops)
                    random.shuffle(final_stops)

                    for selectedFinalStop in final_stops:
                        print("    " * recDepth + f"Selected final stop: {unpackStops(selectedFinalStop['select'])}")
                        stoplist.append(selectedFinalStop["select"])
                        passedstops.append(selectedFinalStop["passed"])
                        # do not recursivbely call, as this route is verified to be possible
                        return linelist, stoplist, passedstops
                    linelist.pop()
                    stoplist.pop()
                    passedstops.pop()
                print("    " * recDepth + f"Stop {unpackStops(selectedStop['select'])} does not work.")
            print("    " * recDepth + f"No stops work with line {selectedLine}, picking another line.")
        # if none of the lines work with any of the stops, return None.
        print("    " * recDepth + f"No lines work, returning None and going to depth {recDepth-1}")
        return None

    

if __name__ == "__main__":
    main()