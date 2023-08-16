import sqlite3
import csv
import os

DIRNAME = os.path.dirname(__file__)

print("What do you want to do?")
print("Enter 1 to update the database.")
print("Enter 2 to synchronize aliases.csv with services.txt.")
action = input("Action: >")

if (action == "2"):
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



