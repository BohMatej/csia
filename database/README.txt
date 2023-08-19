Hello! This folder contains all the data that is used in the mhdle project.

The structure for storing data about lines, stops, and stop service information, is made up of .txt and .csv files inside the /data folder.
The file services.txt is meant to be edited manually, and contains information about which line serves which stops.
    Each line is subdivided into subservices. These reflect the different services that each line may run. 
    Most lines have two subservices, each in the opposite direction. Some have more if they have separate branches, such as lines 4 or 21.
    Some lines only have one subservice, which means they loop without taking a longer break, and it's possible to travel continuously along the subservice.
    Put it that way, each subservice denotes a certain route that can be traveled on the line without having to transfer onto another vehicle.
The file loops.csv denotes which lines loop. It is also meant to be edited manually.
    A line can either have a "tearloop", which means it travels from one terminus along a loop without stopping for a longer time and returns back to the terminus, such as line 1.
    Such service is represented by the number 1.
    If a line loops continouously, it travels in a full loop. We do not have such line in Bratislava, but in case there was to be one added in the future,
    such service would be represented by the number 2.
The file stops.csv has information about each stop, being its unique ID, the district it's in, the "truename", or the stop's name shown on display, and of course, the aliases.
    This file is meant to be edited manually, but the command 3 from dbupdate.py adds the unique ID and alias from services.txt. 
    The district and truename have to be added manually.

The database (mhdle.db) contains multiple tables of data. The data from this database is what the rest of the website uses.
    The 'lines' table contains information about each line: these are the "label" (the line number), the status of whether the line loops, and the color of the line's icon.
    The 'stops' table contains information structured the exact same way as in stops.csv.
    The 'services' table is the most complicated. It stores each stop a line passes through on a subservice. This is best demonstrated by example:
        Take line 4 traveling from Zlate piesky to Dubravka. This subservice of line 4 is denoted by the number 4. 
        The fifth stop on this service is Odborarska, which has an ID of 268. The services_id parameter is dynamically allocated. 
        Hence, a database entry in this table has the following: line_label: 4; stop_id: 268: subservice: 4; order_in_subservice: 5.
        Note that the order_in_subservice starts counting with 0 being the station the vehicles on the subservice first depart from; in this case, stop Zlate Piesky.
    The 'nearstops' table links two different stops with different stop IDs together if they're close enough that transfering by walking between them is feasible.
    The 'sqlite_sequence" table is something created by the sqlite3 library that I'm using and is something I would rather not meddle with. Probably something to do with autoincrement.
If the database file (mhdle.db) does not exist, it can be creating by executing dbinit.py.

However, to actually put the values in the database from the aforementioned .txt and .csv files, you have to run the commands from dbupdate.py.

When running dbupdate.py, you can call many different commands.
Command 1 first starts by calling command 2.
    Then, it gets all infromation about lines and services from services.txt and loops.csv, and puts them in the 'lines' and 'services' tables in the database.
Command 2 only gets the stop aliases from services.txt, and places them in the 'stops' table of the database. You should then manually add each stop's display name and district.
Command 3 is simillar to command 2, but rather than loading into the database, it loads the aliases into stops.csv. 
    Recall that stops.csv and the 'stops' table in the database have the same structure. Also recall how (in the description of stops.csv) I hinted on this command in advance.
Command 4 merges the data from stops.csv into the stops table of the database. 
Command 5 is disfunctional.

A typical edit to the database, in case DPB introduces any changes in their services, should look like this:
    First, manually edit the services.txt and loops.csv files to reflect any changed routing.
    Then call Command 1. This may create incomplete database rows in the 'stops' table if you introduced any new alias in services.txt.
    Finally, go into the mhdle.db database and correct those incomplete rows in the 'stops' table with the appropriate district and truename.

You can use a program such "DB Browser for SQLite" (from sqlitebrowser.org) or any similar one to perform the final step.
However, if that's not possible, commands 3 and 4 do the same thing that command 2 does without forcing you to edit the database manually.
You can use the following procedure to avoid manually accessing the database altogether.
    First, manually edit the services.txt and loops.csv files to reflect any changed routing.
    Then call Command 3. This may create inomplete rows in the stops.csv file, denoted by "DISTRICT" and "TRUENAME" in all caps. Correct these.
    Then, call Command 4 to add the data from stops.csv to the database.
    Finally, call Command 1. Since all aliases have been corrected and added through stops.csv, you can now be sure that there are no holes to fill in the database.
    

