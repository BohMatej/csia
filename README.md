# Computer Science Internal Assessment

To install MHDle on your device, follow, the guide below.

Step 1: If you want to isolate this program from other Python-dependent programs on your device, you will need to install a Python virtual environment using the `python -m venv [PATH]` command. The program is verified to work on Python 3.11.4. Activate this virtual environment using the relevant command available here: https://docs.python.org/3/library/venv.html#how-venvs-work

Step 2: In a command prompt, navigate to the root folder of the application and execute `pip install -r requirements.py.` Alternatively, executing `pip install flask` should install all of Flask's dependencies, as well related libraries such as Flask-Session, Jinja, and Werkzeug.

Step 3: From the root folder of the application and execute `python database/dbinit.py`. This command initializes the SQLite databases.

Step 4: Initially, these databases also need to be populated with line and stop data. From the root folder, execute `python database/dbupdate.py` and when prompted, press 1. Then, execute `python database/dbupdate.py` again, and press 2.

Step 5: Now that all databases have been set up, run the server by executing `flask run` in the terminal. To open the website, navigate to http://127.0.0.1:5000 on your browser.

Step 6: Register an account. The first account to be registered should have admin privileges.
