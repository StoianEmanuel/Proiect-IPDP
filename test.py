from flask import Flask, request, jsonify
import sqlite3
import json
from json import dumps

app = Flask(__name__)

app.config['SQLITE_DB_DIR'] = 'DB'
app.config['SQLITE_DB_NAME'] = 'gaming.db'

# Function to establish connection with the database


def get_db_connection():
    conn = sqlite3.connect('DB\gaming.db')
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
                if int(row[3]) < 1970:
                    count += 1
            elif i == 4 and int(row[4]) == 0:
                count += 1
        game = {
            '@id': row[0],
            'name': row[1],
            'platform': row[2],
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

# Define the route to retrieve all games/consoles


@app.route('/sqlite/gaming/get_data', methods=['GET'])
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

    else:
        # Return error response if data_type is not games or consoles
        error_response = {
            'error': 'Invalid data type'
        }
        return jsonify(error_response), 400


"""
# Retrieve a game from the database by id


def get_game_by_id(id):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videogames WHERE id=?", (id,))
    row = cursor.fetchone()
    if row:
        game = {
            '@id': row[0],
            'name': row[1],
            'platform': row[2],
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
    else:
        game = None
    conn.close()
    return game

# Define the route to retrieve game by id


@app.route('/sqlite/video_games/get_data_by_id', methods=['GET'])
def get_game_data():
    # Check if the id is provided in the query string
    id = request.args.get('id')
    if id is None:
        # Return error response if id is not provided
        error_response = {
            'error': 'id parameter is missing'
        }
        return jsonify(error_response), 400

    # Retrieve game by id
    game = get_game_by_id(id)

    if game is None:
        # Return error response if game is not found
        error_response = {
            'error': 'Game not found'
        }
        return jsonify(error_response), 404

    # Create JSON-LD document
    context = {
        "@schema": "sqlite"
    }
    data = {
        "@context": context,
        "@type": "video games",
        "@list": [game]
    }
    json_ld_doc = json.dumps(data)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response

# Retrieve a console from the database by id


def get_console_by_id(id):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consoles WHERE id=?", (id,))
    row = cursor.fetchone()
    if row:
        console = {
            '@id': row[0],
            'name': row[1],
            'manufacturer': row[2],
            'year_of_release': row[3],
            'sales': row[4],
            'type': row[5],
            'number_of_exclusives': row[6]
        }
    else:
        console = None
    conn.close()
    return console

# Define the route to retrieve console by id


@app.route('/sqlite/consoles/get_data_by_id', methods=['GET'])
def get_console_data():
    # Check if the id is provided in the query string
    id = request.args.get('id')
    if id is None:
        # Return error response if id is not provided
        error_response = {
            'error': 'id parameter is missing'
        }
        return jsonify(error_response), 400

    # Retrieve game by id
    console = get_console_by_id(id)

    if console is None:
        # Return error response if console is not found
        error_response = {
            'error': 'Console not found'
        }
        return jsonify(error_response), 404

    # Create JSON-LD document
    context = {
        "@schema": "sqlite"
    }
    data = {
        "@context": context,
        "@type": "consoles",
        "@list": [console]
    }
    json_ld_doc = json.dumps(data)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response """


if __name__ == '__main__':
    app.run(debug=True, port=8040)
