BEGIN;
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL, 
    hashed_password TEXT NOT NULL,
    time_of_creation NUMERIC NOT NULL
);
CREATE TABLE IF NOT EXISTS dailies (
    user_id INTEGER,
    time_of_guess NUMERIC NOT NULL,
    number_of_guesses INTEGER,
    FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
COMMIT;