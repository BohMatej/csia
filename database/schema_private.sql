BEGIN;
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL, 
    hashed_password TEXT NOT NULL,
    time_of_creation NUMERIC NOT NULL
);
CREATE TABLE IF NOT EXISTS dailyroutes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    routejson TEXT,
    routedate NUMERIC NOT NULL
);
CREATE TABLE IF NOT EXISTS dailyguesses (
    dailyguess_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER,
    user_id INTEGER,
    number_of_guesses INTEGER,
    FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (route_id)
        REFERENCES dailyroutes (route_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
COMMIT;