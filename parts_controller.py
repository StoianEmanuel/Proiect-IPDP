from db import get_db

"""metadata TEXT NOT NULL,                id INTEGER PRIMARY KEY AUTOINCREMENT,   code_producer TEXT,                name TEXT NOT NULL, 
               brand TEXT,                series TEXT,                connections TEXT,                link_address TEXT,
                frequency REAL,                functions TEXT,                weight INTEGER,				price REAL,				resolution TEXT"""
def insert_part(metadata, code_producer, name, brand, series, connections, link_address, frequency, functions, weight,
                price, resolution):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO parts(metadata, code_producer, name, brand, series, connections, link_address, \
        frequency, functions, weight, price, resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(statement, [metadata, code_producer, name, brand, series, connections, link_address, frequency, 
                               functions, weight, price, resolution])
    db.commit()
    return True


def update_part(id, metadata, code_producer, name, brand, series, connections, link_address, frequency, functions, weight,
                price, resolution):
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE parts SET metadata = ?, code_producer = ?, name = ?, brand = ?, series = ?, connections = ?, \
        link_address = ?, frequency = ?, weight = ?, price = ?, resolution = ? WHERE id = ?"
    cursor.execute(statement, [metadata, code_producer, name, brand, series, connections, link_address, frequency, 
                               functions, weight, price, resolution, id])
    db.commit()
    return True


def delete_part(id):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM parts WHERE id = ?"
    cursor.execute(statement, [id])
    db.commit()
    return True


def get_by_id(id):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id, metadata, code_producer, name, brand, series, connections, link_address, \
        frequency, functions, weight, price, resolution FROM parts WHERE id = ?"
    cursor.execute(statement, [id])
    return cursor.fetchone()

def get_by_metadata(metadata):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id, metadata, code_producer, name, brand, series, connections, link_address, \
        frequency, functions, weight, price, resolution FROM parts WHERE metadata = ?"
    cursor.execute(statement, [metadata])
    return cursor.fetchone()

def get_parts():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, metadata, code_producer, name, brand, series, connections, link_address, \
        frequency, functions, weight, price, resolution FROM parts"
    cursor.execute(query)
    return cursor.fetchall()