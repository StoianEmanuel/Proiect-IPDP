from flask import Flask, request, jsonify
import sqlite3
import json
from json import dumps

app = Flask(__name__)

app.config['SQLITE_DB_DIR'] = './'
app.config['SQLITE_DB_NAME'] = 'gaming.sqlite'

# Function to establish connection with the database


def get_db_connection():
    conn = sqlite3.connect('./gaming.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Retrieve all games from the database

def get_all_games(limit=None):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videogames")
    # if limit is None:
    #  cursor.execute("SELECT * FROM videogames")
    # else:
    # cursor.execute("SELECT * FROM videogames LIMIT ?", (limit,))
    rows = cursor.fetchall()
    games = []
    l = 0
    for row in rows:
        count = 0
        for i in range(0, len(row)):
            if i == 1 or i == 2 or i == 4 or i == 5 or i == 15 or i == 16:
                if row[i].upper() == 'NULL' or row[i] == '':
                    count += 1
            elif i == 3 and row[3].upper() != 'N/A':
                if row[3].isnumeric():
                    if int(row[3]) < 1970:
                        count += 1
            elif i == 4 and int(row[4]) == 0:
                count += 1
        game = {
            '@id': row[0],
            'name': row[1],
            'year_of_release': row[3],
            'genre': row[4],
            'publisher': row[5],
            'na_sales': row[6],
            'eu_sales': row[7],
            'jp_sales': row[8],
            'other_sales': row[9],
            'global_sales': row[10],
            'critic_score': row[11],
            'critic_count': row[12],
            'user_score': row[13],
            'user_count': row[14],
            'developer': row[15],
            'rating': row[16]
        }
        if count < 4:
            if limit is None:
                games.append(game)
            elif l < int(limit):
                games.append(game)
                l += 1
    conn.close()
    return games


# Retrieve all consoles from the database


def get_all_consoles(limit=None):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consoles")
    # if limit is None:
    #   cursor.execute("SELECT * FROM consoles")
    # else:
    #   cursor.execute("SELECT * FROM consoles LIMIT ?", (limit,))
    rows = cursor.fetchall()
    consoles = []
    l = 0
    for row in rows:
        count = 0
        for i in range(0, len(row)):
            if i == 1 or i == 2 or i == 5:
                if row[i].upper() == 'NULL' or row[i] == '':
                    count += 1
            elif i == 3 and int(row[3]) < 1970:
                count += 1
            elif i == 4 and int(row[4]) == 0:
                count += 1
        console = {
            '@id': row[0],
            'name': row[1],
            'manufacturer': row[2],
            'year_of_release': row[3],
            'sales': row[4],
            'type': row[5],
            'number_of_exclusives': row[6]
        }
        if count < 3:
            if limit is None:
                consoles.append(console)
            elif l < int(limit):
                consoles.append(console)
                l += 1
    conn.close()
    return consoles

#retrieve all mouses from database
def get_all_mouses(limit=None):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mouses")
    # if limit is None:
    #   cursor.execute("SELECT * FROM mouses")
    # else:
    #   cursor.execute("SELECT * FROM mouses LIMIT ?", (limit,))
    rows = cursor.fetchall()
    mouses = []
    l = 0
    for row in rows:
        count = 0
        for i in range(0, len(row)):
            if i == 1 or i == 2 or i == 4 or i == 3 or i == 6 or i == 8 or i == 10:
                if row[i].upper() == 'NULL' or row[i] == '':
                    count += 1
            elif i == 5 and (int(row[5]) < 3 or int(row[5]) > 20):
                    count += 1
            elif i == 7 and int(row[7]) > 250:
                    count += 1
            elif i == 9 and float(row[9]) > 5:
                    count += 1
        mouse = {
            '@id': row[0],
            'manufacturer': row[1],
            'series': row[2],
            'resolution': row[3],
            'design': row[4],
            'number of buttons': row[5],
            'interface': row[6],
            'weight': row[7],
            'size': row[8],
            'rating': row[9],
            'link address': row[10]
        }
        if count < 4:
            if limit is None:
                mouses.append(mouse)
            elif l < int(limit):
                mouses.append(mouse)
                l += 1
    conn.close()
    return mouses


# Define the route to retrieve all games/consoles


@app.route('/get_data', methods=['GET'])
def get_data():
    # Check if data_type is set to either games or consoles
    data_type = request.args.get('data_type')
    snippet = request.args.get('snippet')
    if data_type == 'consoles':
        # Check if snippet parameter is provided
        if snippet is None:
            # Return error response if snippet parameter is missing
            error_response = {
                'error': 'snippet parameter is missing'
            }
            return jsonify(error_response), 400

        # Retrieve consoles based on the value of snippet parameter
        if snippet.lower() != 'true' and snippet.lower() != 'false':
            error_response = {
                'error': 'snippet parameter does not exists'
            }
            return jsonify(error_response), 404
        if snippet.lower() == 'true':
            # Retrieve first 10 consoles
            consoles = get_all_consoles(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all consoles
            consoles = get_all_consoles()

        # Create JSON-LD document
        context = {
            "@schema": "sqlite/consoles"
        }
        data = {
            "@context": context,
            # "@type": "consoles",
            "@list": consoles
        }
        json_ld_doc = json.dumps(data)

        # Return response in JSON-LD format
        response = app.response_class(
            response=json_ld_doc,
            status=200,
            mimetype='application/ld+json'
        )
        return response

    elif data_type == 'games':
        # Check if snippet parameter is provided
        if snippet is None:
            # Return error response if snippet parameter is missing
            error_response = {
                'error': 'snippet parameter is missing'
            }
            return jsonify(error_response), 400
        # Retrieve games based on the value of snippet parameter
        if snippet.lower() != 'true' and snippet.lower() != 'false':
            error_response = {
                'error': 'snippet parameter does not exists'
            }
            return jsonify(error_response), 400
        if snippet.lower() == 'true':
            # Retrieve first 10 games
            games = get_all_games(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all games
            games = get_all_games()

        # Create JSON-LD document
        context = {
            "@schema": "sqlite/games"
        }
        data = {
            "@context": context,
            # "@type": "video games",
            "@list": games
        }
        json_ld_doc = json.dumps(data)

        # Return response in JSON-LD format
        response = app.response_class(
            response=json_ld_doc,
            status=200,
            mimetype='application/ld+json'
        )
        return response
    
    elif data_type == 'mouses':
        # Check if snippet parameter is provided
        if snippet is None:
            error_response = {
                'error': 'snippet parameter is missing'
            }
            return jsonify(error_response), 400
        # Retrieve mouses based on the value of snippet parameter
        if snippet.lower() != 'true' and snippet.lower() != 'false':
            error_response = {
                'error': 'snippet parameter does not exists'
            }
            return jsonify(error_response), 400
        if snippet.lower() == 'true':
            # Retrieve first 10 mouses
            mouses = get_all_mouses(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all mouses
            mouses = get_all_mouses()

        # Create JSON-LD document
        context = {
            "@schema": "sqlite/games"
        }
        data = {
            "@context": context,
            # "@type": "mouses",
            "@list": mouses
        }
        json_ld_doc = json.dumps(data)

        # Return response in JSON-LD format
        response = app.response_class(
            response=json_ld_doc,
            status=200,
            mimetype='application/ld+json'
        )
        return response
    
    else:
        # Return error response if data_type is not games or consoles or mouses
        error_response = {
            'error': 'Invalid data type'
        }
        return jsonify(error_response), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
