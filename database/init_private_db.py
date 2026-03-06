import os
import sqlite3


DIRNAME = os.path.dirname(__file__)
PRIVATE_DB_PATH = os.path.join(DIRNAME, "mhdle_private.db")
PRIVATE_SCHEMA_PATH = os.path.join(DIRNAME, "schema_private.sql")


def main() -> None:
    conn = sqlite3.connect(PRIVATE_DB_PATH)
    cur = conn.cursor()

    with open(PRIVATE_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        cur.executescript(schema_file.read())

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
