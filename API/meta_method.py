import os
import sqlite3
from flask import Response, json, jsonify


# Get tables names for a database
def get_all_tables(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    # Extrage numele tabelelor din tupluri într-o listă simplă
    table_names = [table[0] for table in tables]

    c.close()
    conn.close()

    return table_names


# Get columns names for table
def get_column_data(db_path = "./Data/gaming.sqlite", table_name = ''):
    conn = sqlite3.connect(db_path)
   
    sql_query = f"PRAGMA table_info({table_name})"   # Define the SQL query to retrieve column names

    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    col_names = [result[1] for result in results]
    
    meta = ",".join(col_names)
    conn.close()
    return meta


# Get all columns name for a database
def get_meta_data(db_path = "./Data/gaming.sqlite"):
    if not os.path.exists(db_path):
        error_response = {"error": "Database does not exist"}
        return jsonify(error_response), 404
    
    table_names = get_all_tables(db_path)
    metadata = {}

    for table_name in table_names:

        # get metadata for every table
        column_data = get_column_data(db_path, table_name)
        change_table_name = table_name

        if change_table_name  in ['platform_mappings', 'sqlite_sequence']:
            continue
        
        if change_table_name == "Consoles":
            column_data = column_data.replace(',Launch Price ($)', '')
        elif change_table_name == "GPU":
            column_data = column_data.replace('Integration Density,', '')

        if change_table_name == "VideoGames":
            change_table_name = "video_games"

        if change_table_name not in ['CPU', 'GPU', 'video_games']:
            change_table_name = change_table_name[0].lower() + change_table_name[1:]
        
        metadata[change_table_name] = column_data

    # Create JSON-LD document
    context = {"@schema": "SQLite"}
    data = {"@context": context, **metadata}
    json_ld_doc = json.dumps(data, indent=4)

    # Return response in JSON-LD format

    response = Response(json_ld_doc, status=200, mimetype="application/ld+json")
    return response