import sqlite3
import csv
import os

DIRNAME = os.path.dirname(__file__)

def main():
    print("What do you want to do?")
    print("Enter 1 to update the database.")
    print("Enter 2 to synchronize aliases from aliases.csv with services.txt (LEGACY).")
    print("Enter 3 to synchronize aliases from stops.csv with services.txt and check for duplicate aliases.")
    action = input("Action: >")

    if (action == "2"):
        updateAliases()
    if (action == "3"):
        updateStops()


def updateStops():
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
    print("Legacy command, use (3) instead.")
    
    '''
    # read existing aliases.csv into variable
    existing_aliases = set()
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "r") as aliases:
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
    
    with open(os.path.join(DIRNAME, "data/aliases.csv"), "a", newline="") as aliases:
        writer = csv.DictWriter(aliases, fieldnames=["alias", "truename"])
        number_of_appends = 0
        for item in to_add_aliases:
            print(item)
            writer.writerow({"alias": item, "truename": ""})
            number_of_appends += 1
        print(f"Append complete. Successfully added {number_of_appends} aliases. Now go correct them!")
        aliases.close()
    '''

if __name__ == "__main__":
    main()