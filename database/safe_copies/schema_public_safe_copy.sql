BEGIN;
CREATE TABLE IF NOT EXISTS stops (
    stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT, 
    truename TEXT
);
CREATE TABLE IF NOT EXISTS aliases (
    alias TEXT UNIQUE ON CONFLICT REPLACE,
    truename TEXT,
    FOREIGN KEY (truename)
        REFERENCES stops (truename)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS lines (
    label TEXT UNIQUE NOT NULL,
    looping_status INTEGER NOT NULL DEFAULT 0,
    /* Looping status: 0 if not looping, 1 if tearlooping, 2 if looping */
    color TEXT NOT NULL DEFAULT "9e9e9e"
);
CREATE TABLE IF NOT EXISTS services (
    services_id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_label TEXT NOT NULL,
    stop_id INTEGER NOT NULL,
    subservice INTEGER NOT NULL,
    order_in_subservice INTEGER,
    UNIQUE (line_label, subservice, order_in_subservice) ON CONFLICT REPLACE
    FOREIGN KEY (line_label)
        REFERENCES lines (label)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (stop_id)
        REFERENCES stops (stop_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS nearstops (
    nearstops_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stopone_id INTEGER,
    stoptwo_id INTEGER,
    walktime INTEGER,
    FOREIGN KEY (stopone_id)
        REFERENCES stops (stop_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
    FOREIGN KEY (stoptwo_id)
        REFERENCES stops (stop_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);
COMMIT;