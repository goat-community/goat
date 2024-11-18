import os

import psycopg

from routing.core.config import settings


def init_db(db_cursor: psycopg.Cursor, db_connection: psycopg.Connection) -> None:
    # Create database functions
    for file in os.listdir("src/db/functions"):
        if file.endswith(".sql"):
            with open(f"src/db/functions/{file}", "r") as f:
                db_cursor.execute(f.read())
                db_connection.commit()


if __name__ == "__main__":
    db_connection = psycopg.connect(settings.POSTGRES_DATABASE_URI)
    db_cursor = db_connection.cursor()
    try:
        init_db(db_cursor, db_connection)
        print("Database initialized.")
    except Exception as e:
        print(e)
        print("Database initialization failed.")
    finally:
        db_connection.close()
