import sqlite3
DATABASE_NAME = "DB\parts.db"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    tables = [
        """CREATE TABLE IF NOT EXISTS parts(
                metadata TEXT NOT NULL,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_producer TEXT,
                name TEXT NOT NULL,
                brand TEXT,
                series TEXT,
                connections TEXT,
                link_address TEXT,
                frequency REAL,
                functions TEXT,
                weight INTEGER,
				price REAL,
				resolution TEXT
            )
            """
    ]
    db = get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute(table)