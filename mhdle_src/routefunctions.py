from typing import Tuple, List
from helpers import *
import random

def main():
    #generateRoute(5, useGreyLines=True)
    generateRoute(2,area=("devin",), useGreyLines=True)
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
        global SUCCESSCONDITION
        SUCCESSCONDITION = False
        print(generateFirstLines(area, useGreyLines))
        return
        print(f"Starting standardGeneration of length {length}.")
        linelist, stoplist = standardGeneration(1, length, area, useGreyLines, linelist, stoplist, False)


def standardGeneration(
        recDepth: int,
        length: int, 
        area: Tuple[str, ...], 
        useGreyLines: bool,
        linelist: List[str],
        stoplist: List[int],
        ) -> Tuple[Tuple[str, ...], Tuple[int, ...]]:

    # declare use of global
    global SUCCESSCONDITION
    print(recDepth)
    # base case: where the first line and stop is generated
    if (recDepth == 1):

        # generate first line
        lines = random.shuffle(generateFirstLines(area, useGreyLines))

        for selectedLine in lines:
            # generate first stop
            stops = random.shuffle(generateFirstStops(area, useGreyLines, selectedLine))

            for selectedStop in stops:
                # if length > 1, then more lines and stops still have to be generated.
                if length > 1:
                    if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                        linelist.append(selectedLine)
                        stoplist.append(selectedStop)
                        # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                        returntuple = standardGeneration(recDepth+1, length, area, useGreyLines, linelist, stoplist)
                        if returntuple is not None:
                            return linelist, stoplist
                        else:
                            linelist.pop()
                            stoplist.pop()
                # if length == 1, then the last (core) line and stop has to be added, alongside a final stop
                else:
                    if finalStopIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # does not require transfer
                        linelist.append(selectedLine)
                        stoplist.append(selectedStop)
                        stoplist.append(random.choice(generateFinalStops))
                        # set true successCondition
                        SUCCESSCONDITION = True
                        # do not recursivbely call, as the route of length 1 is verified to be possible
                        return linelist, stoplist
        # if none of the lines work
        print("Sorry, the conditions for the route you picked can't generate a route.")
        return None
    
    # core (or final) case
    else:
        # generate core line
        lines = random.shuffle(generateCoreLines(area, useGreyLines, linelist, stoplist))

        for selectedLine in lines:
            # generate core stop
            stops = random.shuffle(generateCoreStops(area, useGreyLines, linelist, stoplist, selectedLine))

            for selectedStop in stops:
                # if length > recDepth, then more lines and stops still have to be generated.
                if length > recDepth:
                    if transferIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # requires transfer
                        linelist.append(selectedLine)
                        stoplist.append(selectedStop)
                        # recursively call standardGeneration at a "higher" depth (really, the function is at its deepest at recDepth = 0)
                        returntuple = standardGeneration(recDepth+1, length, area, useGreyLines, linelist, stoplist)
                        if returntuple is not None:
                            return linelist, stoplist
                        else:
                            linelist.pop()
                            stoplist.pop()
                # if length == recDepth, then the last (core) line and stop has to be added, alongside a final stop
                else:
                    if finalStopIsPossible(area, linelist, stoplist, selectedLine, selectedStop): # does not require transfer
                        linelist.append(selectedLine)
                        stoplist.append(selectedStop)
                        stoplist.append(random.choice(generateFinalStops))
                        # set true successCondition
                        SUCCESSCONDITION = True
                        # do not recursivbely call, as this route is verified to be possible
                        return linelist, stoplist




    



            
    

    

if __name__ == "__main__":
    main()