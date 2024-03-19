import sqlite3
import csv
import os
from itertools import chain

DIRNAME = os.path.dirname(__file__)

def main():
    print("What do you want to do?")
    print("Enter 1 to load stops to the database.")
    print("Enter 2 to to load services, nearstops, and loops to the database.")

    action = input("Action: >")

    if (action == "1"):
        DatabaseUpdate.updateStopsDatabase()
    if (action == "2"):
        DatabaseUpdate.updateAllDatabase()
    
    x = input()


class DatabaseUpdate():
    def updateAllDatabase():

        # establishes DB connection
        conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
        cur = conn.cursor()

        # These lists each contain tuples of values, which will later be used in queries.
        lines_tuples = []
        colors_tuples = []
        services_tuples = []

        
        # read services.txt
        with open(os.path.join(DIRNAME, "data/services.txt"), "r") as services:
            rownumber = 1
            linenumber = None
            subservicenumber = None
            order_in_subservice = 0
            color = None

            # loop through rows in services.txt
            for row in services:
                row = row.strip().split(" ")
                print(row)

                # ignore newlines in services.txt
                if len(row[0]) == 0:
                    rownumber += 1
                    continue

                # sort out tags
                if row[0][0] == "/":
                    if row[0] == "/line":
                        if subservicenumber != None or color != None:
                            print(f"Error on line {rownumber} of services.txt. Subservice or color not 'None' for /line tag. Please fix.")
                            return
                        subservicenumber = None
                        linenumber = row[1]
                        lines_tuples.append((linenumber,))
                    elif row[0] == "/subservice":
                        if linenumber == None:
                            print(f"Error on line {rownumber} of services.txt. Line number not set for /subservice tag. Please fix.")
                            return
                        try:
                            temp = int(row[1])
                        except ValueError:
                            print(f"Error on line {rownumber} of services.txt. Subservice is not an integer. Please fix.")
                            return
                        order_in_subservice = 0
                        if subservicenumber == None and temp != 1:
                            print(f"Error on line {rownumber} of services.txt. Subservice does not begin at 1. Please fix.")
                            return
                        if subservicenumber != None:
                            if temp != subservicenumber + 1:
                                print(f"Error on line {rownumber} of services.txt. Subservice does not increase by 1. Please fix.")
                                return
                        subservicenumber = temp
                    elif row[0] == "/color":
                        if linenumber == None:
                            print(f"Error on line {rownumber} of services.txt. Line number not set for /color tag. Please fix.")
                            return
                        color = row[1]
                        colors_tuples.append((color, linenumber,))
                elif row[0][0] == "]":
                    if linenumber == None:
                        print(f"Error on line {rownumber} of services.txt. Probably an extra bracket. Please fix.")
                        return
                elif row[0][0] == "}":
                    linenumber = None
                    color = None
                    subservicenumber = None
                    
                # sort out each subservice's stops
                else:
                    stop_id = " ".join(row)
                    services_tuples.append((linenumber, stop_id, subservicenumber, order_in_subservice,))
                    order_in_subservice += 1
                rownumber += 1

        # read loops.csv
        loops_tuples = []
        with open(os.path.join(DIRNAME, "data/loops.csv"), "r", encoding="utf-8") as loops:
            reader = csv.DictReader(loops)
            for row in reader:
                loops_tuples.append((row["looptype"], row["alias"],))
        
        # read nearstops.csv
        nearstops_tuples = []
        with open(os.path.join(DIRNAME, "data/nearstops.csv"), "r", encoding="utf-8") as nearstops:
            reader = csv.DictReader(nearstops)
            rownumber = 2
            for row in reader:
                stopone_id = row["first"]
                stoptwo_id = row["second"]
                if stopone_id == None:
                    print(f"Error in nearstops, at line {rownumber}: column \"first\" has undefined stop ID \"{row['first']}\".")
                    return
                if stoptwo_id == None:
                    print(f"Error in nearstops, at line {rownumber}: column \"second\" has undefined ID \"{row['second']}\".")
                    return
                nearstops_tuples.append((stopone_id, stoptwo_id, row["walktime"]))
                rownumber += 1



        # execute query on lines table
        cur.executemany("INSERT OR REPLACE INTO lines (label) VALUES (?)", lines_tuples)

        # execute query on lines table, adding line color
        cur.executemany("UPDATE lines SET color = ? WHERE label = ?", colors_tuples)

        # execute query on lines table, adding line looping status
        cur.executemany("UPDATE lines SET looping_status = ? WHERE label = ?", loops_tuples)

        # execute query on nearstops table
        cur.executemany("INSERT OR REPLACE INTO nearstops (stopone_id, stoptwo_id, walktime) VALUES (?, ?, ?)", nearstops_tuples)

        # execute query on services table
        cur.executemany("INSERT OR REPLACE INTO services (line_label, stop_id, subservice, order_in_subservice) VALUES (?, ?, ?, ?)", services_tuples)
            
        # execute query to remove unwanted values from lines table
        mylist = []
        for tuple in lines_tuples:
            mylist.append(tuple[0])
        cur.execute("DELETE FROM lines WHERE label NOT IN (%s)" % ','.join('?'*len(mylist)), mylist)

        # execute query to remove unwanted values from services table
        mylist = []
        for tuple in services_tuples:
            mylist.append(cur.execute("""SELECT services_id FROM services 
                                    WHERE line_label = ?
                                    AND stop_id = ?
                                    AND subservice = ?
                                    AND order_in_subservice = ?""", tuple).fetchone()[0])
        cur.execute("DELETE FROM services WHERE services_id NOT IN (%s)" % ','.join('?'*len(mylist)), mylist)

        # execute query to remove unwanted values from nearstops table
        mylist = []
        for tuple in nearstops_tuples:
            mylist.append(cur.execute("""SELECT nearstops_id FROM nearstops 
                                    WHERE stopone_id = ?
                                    AND stoptwo_id = ?
                                    AND walktime = ?""", tuple).fetchone()[0])
        cur.execute("DELETE FROM nearstops WHERE nearstops_id NOT IN (%s)" % ','.join('?'*len(mylist)), mylist)

        # commit queries
        conn.commit()

        # closes database
        cur.close()
        conn.close()


    def updateStopsDatabase():
        conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
        cur = conn.cursor()
        
        # read stops.csv and add stop uids, districts, and truenames
        list_of_tuples = []
        with open(os.path.join(DIRNAME, "data/stops.csv"), "r", encoding="utf-8") as stops:
            reader = csv.DictReader(stops)
            for row in reader:
                list_of_tuples.append((row["uid"], row["district"], row["truename"]))
        
        # execute DB query
        cur.executemany("""INSERT INTO stops (stop_id, district, truename) VALUES (?,?,?) 
                        ON CONFLICT DO UPDATE SET district=excluded.district, truename=excluded.truename""", list_of_tuples)
        
        conn.commit()
        cur.close()
        conn.close()

        print(f"Successfully added data from stops.csv to the database's 'stops' table.")

if __name__ == "__main__":
    main()