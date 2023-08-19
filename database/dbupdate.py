import sqlite3
import csv
import os
from itertools import chain

DIRNAME = os.path.dirname(__file__)

def main():
    print("What do you want to do?")
    print("Enter 1 to update the database.")
    print("Enter 2 to load all stop aliases from services.txt to the database.")
    print("Enter 3 to synchronize aliases from stops.csv with services.txt and check for duplicate aliases (LEGACY).")
    print("Enter 4 to synchronize aliases from aliases.csv with services.txt (NOT FUNCTIONAL).")
    print("Enter 5 to load stops.csv into the database's stops table (LEGACY).")

    action = input("Action: >")

    if (action == "1"):
        updateAllDatabase()
    if (action == "2"):
        updateStopsDatabase()
    if (action == "3"):
        updateStopsCSV()
    if (action == "4"):
        updateAliases()
    if (action == "5"):
        loadStops()


def updateAllDatabase():

    # calls updateStopsDatabase to establish relation between alias and stopID. District and truename are not necessary just yet.
    updateStopsDatabase()

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
                stop_id = cur.execute("SELECT stop_id FROM stops WHERE alias = ?", (row[0],)).fetchone()[0]
                services_tuples.append((linenumber, stop_id, subservicenumber, order_in_subservice,))
                order_in_subservice += 1

            rownumber += 1

    # execute query on lines table
    cur.executemany("INSERT OR REPLACE INTO lines (label) VALUES (?)", lines_tuples)

    # execute query on lines table, adding line color
    cur.executemany("UPDATE lines SET color = ? WHERE label = ?", colors_tuples)


    # execute query on services table
    cur.executemany("INSERT OR REPLACE INTO services (line_label, stop_id, subservice, order_in_subservice) VALUES (?, ?, ?, ?)", services_tuples)
                
    # execute query to remove unwanted values from lines table
    mylist = []
    for tuple in lines_tuples:
        mylist.append(tuple[0])
    cur.execute("DELETE FROM lines WHERE label NOT IN (%s)" % ','.join('?'*len(mylist)), mylist)

    # execute query to remove unwanted values from services table
    temp_line_label = []
    temp_stop_id = []
    temp_subservice = []
    temp_order = []
    for tuple in services_tuples:
        temp_line_label.append(tuple[0])
        temp_stop_id.append(tuple[1])
        temp_subservice.append(tuple[2])
        temp_order.append(tuple[3])
    temp_master = chain(temp_line_label, temp_stop_id, temp_subservice, temp_order)
    temp_master = (*temp_master, )
    
    mylist = cur.execute("""SELECT services_id FROM services 
                         WHERE line_label IN (%s) 
                         AND stop_id IN (%s) 
                         AND subservice IN (%s) 
                         AND order_in_subservice IN (%s)""" % (','.join('?'*len(services_tuples)), 
                                                               ','.join('?'*len(services_tuples)), 
                                                               ','.join('?'*len(services_tuples)), 
                                                               ','.join('?'*len(services_tuples))),
                                                               temp_master).fetchall()
    myactualfuckinglist = []
    for tuple in mylist:
        myactualfuckinglist.append(tuple[0])
    cur.execute("DELETE FROM services WHERE services_id NOT IN (%s)" % ','.join('?'*len(myactualfuckinglist)), myactualfuckinglist)

    # commit queries
    conn.commit()

    # closes database
    cur.close()
    conn.close()


def updateStopsDatabase():
    conn = sqlite3.connect(os.path.join(DIRNAME, "mhdle.db"))
    cur = conn.cursor()

    # read services.txt and add stop aliases
    list_of_tuples = []
    with open(os.path.join(DIRNAME, "data/services.txt"), "r") as services:
        for line in services:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] in ["]", "}", "/"]:
                continue
            list_of_tuples.append((line,))
    
    # execute DB query
    cur.executemany("INSERT INTO stops (alias) VALUES (?) ON CONFLICT DO NOTHING", list_of_tuples)
    conn.commit()
        
    cur.close()
    conn.close()

    print(f"Successfully added entries. Now go into the database and fix them!")


def updateStopsCSV():

    # read existing stop aliases from stops.csv into variable
    existing_aliases = set()
    maximum_uid = 0
    duplicate_aliases = set()
    with open(os.path.join(DIRNAME, "data/stops.csv"), "r", encoding="utf-8") as stops:
        reader = csv.DictReader(stops)
        for row in reader:
            # check and warn for duplicate aliases
            if row["alias"] in existing_aliases:
                duplicate_aliases.add(row["alias"])
            existing_aliases.add(row["alias"])
            maximum_uid = int(row["uid"])

    # read services and select which aliases to add to stops.csv
    to_add_aliases = set()
    with open(os.path.join(DIRNAME, "data/services.txt"), "r") as services:
        for line in services:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] in ["]", "}", "/"]:
                continue
            if line in existing_aliases:
                continue
            to_add_aliases.add(line)
    
    # write new aliases into stops.csv
    number_of_appends = 0
    with open(os.path.join(DIRNAME, "data/stops.csv"), "a", newline="") as aliases:
        writer = csv.DictWriter(aliases, fieldnames=["uid", "district", "truename", "alias"])
        for item in to_add_aliases:
            writer.writerow({"uid": maximum_uid+1, "district": "DISTRICT", "alias": item, "truename": "TRUENAME"})
            number_of_appends += 1
            maximum_uid += 1

    #print out results
    print("")
    if number_of_appends == 0:
        print("All aliases from services.txt are already present in stops.csv.")
    else:
        print(f"Sync complete. Successfully added {number_of_appends} aliases. Now go correct them!")

    # warn user of duplicate aliases
    if len(duplicate_aliases) == 0:
        print("No duplicate aliases have been found.")
    else:
        print(f"{len(duplicate_aliases)} duplicate aliases found:")
        for alias in duplicate_aliases:
            print(alias)
    
    aliases.close()


def updateAliases():
    print("Disfuncional command, use (3) instead.")
    
    '''
    # read existing aliases.csv into variable
    existing_aliases = set()
    with open(os.path.join(DIRNAME, "data/legacy/aliases.csv"), "r") as aliases:
        reader = csv.DictReader(aliases)
        for row in reader:
            existing_aliases.add(row["alias"])

    # read services and select which aliases to add to aliases.csv
    to_add_aliases = set()
    with open(os.path.join(DIRNAME, "data/services.txt"), "r") as services:
        for line in services:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] in ["]", "}", "/"]:
                continue
            if line in existing_aliases:
                continue
            to_add_aliases.add(line)
    
    with open(os.path.join(DIRNAME, "data/legacy/aliases.csv"), "a", newline="") as aliases:
        writer = csv.DictWriter(aliases, fieldnames=["alias", "truename"])
        number_of_appends = 0
        for item in to_add_aliases:
            print(item)
            writer.writerow({"alias": item, "truename": ""})
            number_of_appends += 1
        print(f"Append complete. Successfully added {number_of_appends} aliases. Now go correct them!")
        aliases.close()
    '''


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