from flask import Flask, request, jsonify
import sqlite3
import json
from json import dumps

app = Flask(__name__)

app.config['SQLITE_DB_DIR'] = 'DB'
app.config['SQLITE_DB_NAME'] = 'VideoGames.db'

# Retrieve all videoGames from the database
def get_all_games():
    conn = sqlite3.connect(
        f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VideoGames")
    rows = cursor.fetchall()
    videoGames = []
    for row in rows:
        videoGame = {
            'id': row[0],
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
        videoGames.append(videoGame)
    conn.close()
    return videoGames

# Function to establish connection with the database
def get_db_connection():
    conn = sqlite3.connect('VideoGames.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define the route to retrieve all games
@app.route('/games', methods=['GET'])
def get_games():
    data_type = request.args.get('data_type')
    if data_type != 'games':
        # Return error response if data_type is not books
        error_response = {
            'error': 'Invalid data type'
        }
        return jsonify(error_response), 400

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

# Function to get a game by id
@app.route('/games/get_data', methods=['GET'])
def get_game_by_id():
    game_id = request.args.get('id')
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE id = ?',
                        (game_id,)).fetchone()
    conn.close()
    if game is None:
        return jsonify({'error': 'Game not found'}), 404
    game_dict = dict(game)
    game_dict['@context'] = 'https://schema.org/'
    game_dict['@type'] = 'Game'
    return dumps(game_dict)

# Function to add a new game


@app.route('/games', methods=['POST'])
def add_game():
    conn = get_db_connection()
    game_data = request.json
    game = (game_data['name'], game_data['platform'], game_data['year_of_release'], game_data['genre'], game_data['publisher'], game_data['na_sales'],
            game_data['eu_sales'], game_data['jp_sales'], game_data['other_sales'], game_data['global_sales'], game_data['critic_score'],
            game_data['critic_count'], game_data['user_score'], game_data['user_count'], game_data['developer'], game_data['rating'])
    conn.execute('INSERT INTO games (name, platform, year_of_release, genre, publisher, na_sales, eu_sales, jp_sales, other_sales, global_sales, critic_score, critic_count, user_score, user_count, developer, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', game)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Game added successfully'}), 201

# Function to update a game


@app.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    conn = get_db_connection()
    game_data = request.json
    game = (game_data['name'], game_data['platform'], game_data['year_of_release'], game_data['genre'], game_data['publisher'], game_data['na_sales'],
            game_data['eu_sales'], game_data['jp_sales'], game_data['other_sales'], game_data['global_sales'], game_data['critic_score'],
            game_data['critic_count'], game_data['user_score'], game_data['user_count'], game_data['developer'], game_data['rating'], game_id)
    conn.execute('UPDATE games SET name = ?, platform = ?, year_of_release = ?, genre = ?, publisher = ?, na_sales = ?, eu_sales = ?, other_sales = ?, global_sales = ?, critic_score = ?, critic_count = ?, user_score = ?, user_count = ?, developer = ?, rating = ? WHERE id = ?', game)
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
    return jsonify({'message': 'Game deleted successfully'})


if __name__ == '__main__':
    app.run(port=5900)
