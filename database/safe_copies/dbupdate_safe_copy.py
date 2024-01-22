import sqlite3
import csv
import os
from itertools import chain

DIRNAME = os.path.dirname(__file__)

def main():
    print("What do you want to do?")
    print("Enter 1 to to synchronize aliases from aliases.csv with services.txt.")
    print("Enter 2 to to synchronize truenames from stops.csv with aliases.csv.")
    print("Enter 3 to to load everything to the database.")
    print("Enter 4 to load stops.csv into the database's stops table (LEGACY).")

    action = input("Action: >")

    if (action == "1"):
        updateAliasesCSV()
    if (action == "2"):
        updateStopsCSV()
    if (action == "3"):
        updateAllDatabase()
    if (action == "4"):
        loadStops()
    
    x = input()



def updateAllDatabase():

    # calls updateStopsDatabase to establish relation between alias and stopID. District and truename are not necessary just yet.
    updateStopsDatabase()
    print("")

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
                    #cur.execute("INSERT INTO lines (label) VALUES (?) ON CONFLICT DO NOTHING", (linenumber,))
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
                    #cur.execute("UPDATE lines SET color = ? WHERE label = ?", (color, linenumber,))
                    colors_tuples.append((color, linenumber,))
            elif row[0][0] == "]":
                if linenumber == None:
                    print(f"Error on line {rownumber} of services.txt. Probably an extra bracket. Please fix.")
                    return
            elif row[0][0] == "}":
                linenumber = None
                color = None
                subservicenumber = None
            elif len(row) > 1:
                print(f"Error on line {rownumber} of services.txt. Wrongly structured line. Please fix.")
                return
            
            # sort out each subservice's stops
            else:
                stop_id = cur.execute("SELECT stop_id FROM stops WHERE truename = (SELECT truename FROM aliases WHERE alias = ?)", (row[0],)).fetchone()[0]
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
            stopone_id = cur.execute("SELECT stop_id FROM stops WHERE truename = (SELECT truename FROM aliases WHERE alias = ?)", (row["first"],)).fetchone()
            stoptwo_id = cur.execute("SELECT stop_id FROM stops WHERE truename = (SELECT truename FROM aliases WHERE alias = ?)", (row["second"],)).fetchone()
            if stopone_id == None:
                print(f"Error in nearstops, at line {rownumber}: column \"first\" has undefined stop alias \"{row['first']}\".")
                print("This stop alias is not present neither in the database, nor in services.txt.")
                return
            if stoptwo_id == None:
                print(f"Error in nearstops, at line {rownumber}: column \"second\" has undefined alias \"{row['second']}\".")
                print("This stop alias is not present neither in the database, nor in services.txt.")
                return
            nearstops_tuples.append((stopone_id[0], stoptwo_id[0], row["walktime"]))
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

    # read aliases.csv and add stop aliases and truenames
    list_of_tuples = []
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "r", encoding="utf-8") as aliases:
        reader = csv.DictReader(aliases)
        for row in reader:
            list_of_tuples.append((row["alias"],row["truename"]))
    
    # execute DB query
    cur.executemany("INSERT INTO aliases (alias, truename) VALUES (?,?) ON CONFLICT DO NOTHING", list_of_tuples)
    
    # read stops.csv and add stop uids, districts, and truenames
    list_of_tuples = []
    with open(os.path.join(DIRNAME, "data/stops.csv"), "r", encoding="utf-8") as stops:
        reader = csv.DictReader(stops)
        for row in reader:
            list_of_tuples.append((row["uid"], row["district"], row["truename"]))
    
    # execute DB query
    cur.executemany("INSERT INTO stops (stop_id, district, truename) VALUES (?,?,?) ON CONFLICT DO NOTHING", list_of_tuples)
    
    conn.commit()
    cur.close()
    conn.close()

    print(f"Successfully added data from stops.csv and aliases.csv to the database's 'stops' and 'aliases' tables.")


def updateStopsCSV():

    # read existing stop truenames from stops.csv into variable
    existing_truenames = set()
    maximum_uid = 0
    duplicate_truenames = set()
    with open(os.path.join(DIRNAME, "data/stops.csv"), "r", encoding="utf-8") as stops:
        reader = csv.DictReader(stops)
        for row in reader:
            # check and warn for duplicate aliases
            if row["truename"] in existing_truenames:
                duplicate_truenames.add(row["truename"])
            existing_truenames.add(row["truename"])
            maximum_uid = int(row["uid"])

    # read aliases.csv and select which truenames to add to stops.csv
    to_add_truenames = set()
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "r", encoding="utf-8") as aliases:
        reader = csv.DictReader(aliases)
        for row in reader:
            if row["truename"] in existing_truenames:
                continue
            to_add_truenames.add(row["truename"])
    
    # write new aliases into stops.csv
    number_of_appends = 0
    with open(os.path.join(DIRNAME, "data/stops.csv"), "a", newline="") as stops:
        writer = csv.DictWriter(stops, fieldnames=["uid", "district", "truename"])
        for item in to_add_truenames:
            writer.writerow({"uid": maximum_uid+1, "district": "DISTRICT", "truename": item})
            number_of_appends += 1
            maximum_uid += 1

    #print out results
    print("")
    if number_of_appends == 0:
        print("All aliases from services.txt are already present in stops.csv.")
    else:
        print(f"Sync complete. Successfully added {number_of_appends} aliases into the stops.csv file. Now go correct them!")

    # warn user of duplicate aliases
    if len(duplicate_truenames) == 0:
        print("No duplicate stops have been found.")
    else:
        print(f"{len(duplicate_truenames)} duplicate stops found:")
        for truename in duplicate_truenames:
            print(truename)
    
    aliases.close()


def updateAliasesCSV():
    # read existing aliases.csv into variable
    existing_aliases = set()
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "r", encoding="utf-8") as aliases:
        reader = csv.DictReader(aliases)
        for row in reader:
            existing_aliases.add(row["alias"])
    # read services and select which aliases to add to aliases.csv
    to_add_aliases = set()
    with open(os.path.join(DIRNAME, "data/services.txt"), "r", encoding="utf-8") as services:
        for line in services:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] in ["]", "}", "/"]:
                continue
            if line in existing_aliases:
                continue
            to_add_aliases.add(line)
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "a", encoding="utf-8", newline="") as aliases:
        writer = csv.DictWriter(aliases, fieldnames=["alias", "truename"])
        number_of_appends = 0
        for item in to_add_aliases:
            print(item)
            writer.writerow({"alias": item, "truename": ""})
            number_of_appends += 1
        print(f"Append complete. Successfully added {number_of_appends} aliases. Now go correct them!")
        aliases.close()


def loadStops():
    conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
    cur = conn.cursor()

    with open(os.path.join(DIRNAME, "data/stops.csv"), "r", encoding="utf-8") as stops:
        reader = csv.DictReader(stops)
        for row in reader:
            # check and warn for duplicate aliases
            cur.execute("INSERT INTO stops (stop_id, district, truename, alias) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING;", (row["uid"], row["district"], row["truename"], row["alias"]))
            conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()