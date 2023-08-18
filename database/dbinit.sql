BEGIN;
CREATE TABLE IF NOT EXISTS stops (
    stop_id INTEGER,
    district TEXT, 
    truename TEXT,
    alias TEXT
);
COMMIT;