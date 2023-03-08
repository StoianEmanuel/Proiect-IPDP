from flask import Flask, request, jsonify
import sqlite3
import json
from json import dumps

app = Flask(__name__)

app.config['SQLITE_DB_DIR'] = 'DB'
app.config['SQLITE_DB_NAME'] = 'games.db'

# Retrieve all games from the database


def get_all_games(limit=None):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    if limit is None:
        cursor.execute("SELECT * FROM games")
    else:
        cursor.execute("SELECT * FROM games LIMIT ?", (limit,))
    rows = cursor.fetchall()
    games = []
    for row in rows:
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
        games.append(game)
    conn.close()
    return games

# Function to establish connection with the database


def get_db_connection():
    conn = sqlite3.connect('DB\games.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define the route to retrieve all games


@app.route('/get_data', methods=['GET'])
def get_data():
    # Check if data_type is set to games
    data_type = request.args.get('data_type')
    if data_type != 'games':
        # Return error response if data_type is not games
        error_response = {
            'error': 'Invalid data type'
        }
        return jsonify(error_response), 400

    # Retrieve up to 100 games
    # limit = min(request.args.get('limit', default=10, type=int), 10)
    # games = get_all_games(limit=limit)

    # Retrieve all games
    games = get_all_games()

    # Create JSON-LD document
    context = {
        "@schema": "sqlite"
    }
    data = {
        "@context": context,
        "@type": "games",
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

# Retrieve a game from the database by id


def get_game_by_id(id):
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE id=?", (id,))
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


@app.route('/games/get_data', methods=['GET'])
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
        "@type": "games",
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


"""
# Function to add a new game


@app.route('/games', methods=['POST'])
def add_game():
    conn = get_db_connection()
    game_data = request.json
    game = (game_data['name'], game_data['platform'], game_data['year_of_release'], game_data['genre'], game_data['publisher'], game_data['na_sales'], game_data['eu_sales'], game_data['jp_sales'],
            game_data['other_sales'], game_data['global_sales'], game_data['critic_score'], game_data['critic_count'], game_data['user_score'], game_data['user_count'], game_data['developer'], game_data['rating'])
    conn.execute('INSERT INTO games (name, platform, year_of_release, genre, publisher, na_sales, eu_sales, jp_sales, other_sales, global_sales, critic_score, critic_count, user_score, user_count, developer, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', game)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Game added successfully'}), 201

# Function to update a game


@app.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    conn = get_db_connection()
    game_data = request.json
    game = (game_data['name'], game_data['platform'], game_data['year_of_release'], game_data['genre'], game_data['publisher'], game_data['na_sales'], game_data['eu_sales'], game_data['jp_sales'],
            game_data['other_sales'], game_data['global_sales'], game_data['critic_score'], game_data['critic_count'], game_data['user_score'], game_data['user_count'], game_data['developer'], game_data['rating'], game_id)
    conn.execute('UPDATE games SET name = ?, platform = ?, year_of_release = ?, genre = ?, publisher = ?, na_sales = ?, eu_sales = ?, jp_sales = ?, other_sales = ?, global_sales = ?, critic_score = ?, critic_count = ?, user_score = ?, user_count = ?, developer = ?, reting = ? WHERE id = ?', game)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Game updated successfully'})

# Function to delete a game

@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM games WHERE id = ?', (game_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Game deleted successfully'})"""


if __name__ == '__main__':
    app.run(port=8010)
