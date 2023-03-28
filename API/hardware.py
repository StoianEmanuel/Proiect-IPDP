from flask import Flask, request, jsonify
import sqlite3
import json
import os
from json import dumps

app = Flask(__name__)
host = os.getenv('HOST', '127.0.0.1')   #change maybe to 0.0.0.0
port = int(os.getenv('PORT', '7090'))

# Function to establish connection with the database

def get_db_connection():
    conn = sqlite3.connect('../Data/gaming.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Retrieve all games from the database

def get_all_games(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videogames")
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
            '@Id': row[0],
            'Name': row[1],
            'Year of Release': row[3],
            'Genre': row[4],
            'Publisher': row[5],
            'North America Sales': row[6],
            'Europe Sales': row[7],
            'Japan Sales': row[8],
            'Other Sales': row[9],
            'Global Sales': row[10],
            'Critic Score': row[11],
            'Critic Count': row[12],
            'User Score': row[13],
            'User Count': row[14],
            'Developer': row[15],
            'Rating': row[16]
        }
        if count < 4:
            if limit is None:
                games.append(game)
            elif l < int(limit):
                games.append(game)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return games


# Retrieve all consoles from the database


def get_all_consoles(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consoles")
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
            '@Id': row[0],
            'Name': row[1],
            'Manufacturer': row[2],
            'Year of Release': row[3],
            'Sales': row[4],
            'Type': row[5],
            'Number of Exclusives': row[6]
        }
        if count < 3:
            if limit is None:
                consoles.append(console)
            elif l < int(limit):
                consoles.append(console)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return consoles

#Retrieve all mice from database

def get_all_mice(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mice")
    rows = cursor.fetchall()
    mice = []
    l = 0
    for row in rows:
        count = 0
        for i in range(0, len(row)):
            if i == 1 or i == 2 or i == 4 or i == 3 or i == 6 or i == 8 or i == 10: # i == 11 or i == 12 or i == 13
                if row[i].upper() == 'NULL' or row[i] == '':
                    count += 1
            elif i == 5:
                if not row[5]:
                    count += 1
                elif row[5] and int(row[5]) < 3 or int(row[5]) > 20:
                    count += 1
            elif i == 7:
                if not row[7]:
                    count += 1
                elif row[7] and int(row[7]) > 250:
                    count += 1
            elif i == 9:
                if not row[9]:
                    count += 1
                elif row[9] and float(row[9]) > 5:
                    count += 1
        mouse = {
            '@Id': row[0],
            'Manufacturer': row[1],
            'Model': row[2],
            'Resolution': row[3],
            'Design': row[4],
            'Number of Buttons': row[5],
            'Interface': row[6],
            'Weight': row[7],
            'Size': row[8], #Size (L x W x H) in mm
            'Rating': row[9],
            'Link Address': row[10] #'Battery Type': row[11],             'Designed for': row[12],             'Extra Functions': row[13] 
        }
        if count < 4:
            if limit is None:
                mice.append(mouse)
            elif l < int(limit):
                mice.append(mouse)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return mice


# Define the route to retrieve all games/consoles/mice

@app.route('/get_data', methods=['GET'])
def get_data():
    # Check if data_type is set to either games or consoles
    data_type = request.args.get('data_type')
    snippet = request.args.get('snippet')
    if data_type != "mice" and data_type != "consoles" and data_type != "video_games":
        # Return error response if data_type is not games or consoles or mice
        error_response = {
            'error': 'Invalid data type'
        }
        return jsonify(error_response), 400
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
    if data_type == 'consoles':
        if snippet.lower() == 'true':
            # Retrieve first 10 consoles
            consoles = get_all_consoles(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all consoles
            consoles = get_all_consoles()

        # Create JSON-LD document
        context = {
            "@schema": "SQLite/consoles"
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

    elif data_type == 'video_games':
        if snippet.lower() == 'true':
            # Retrieve first 10 games
            games = get_all_games(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all games
            games = get_all_games()

        # Create JSON-LD document
        context = {
            "@schema": "SQLite/games"
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
    
    elif data_type == 'mice':
        if snippet.lower() == 'true':
            # Retrieve first 10 mice
            mice = get_all_mice(limit=10)
        elif snippet.lower() == 'false':
            # Retrieve all mice
            mice = get_all_mice()

        # Create JSON-LD document
        context = {
            "@schema": "SQLite/games"
        }
        data = {
            "@context": context,
            # "@type": "mice",
            "@list": mice
        }
        json_ld_doc = json.dumps(data)

        # Return response in JSON-LD format
        response = app.response_class(
            response=json_ld_doc,
            status=200,
            mimetype='application/ld+json'
        )
        return response

#Method to get meta for the database
@app.route('/get_meta')
def get_meta():
    # Create JSON-LD document
    context = {
        "@schema": "SQLite"
    }
    data = {
        "@context": context,
        "consoles": "Id,Name,Manufacturer,Year of Release,Sales,Type,Number of Exclusives",
        "video_games": "Id,Name,Year of Release,Genre,Publisher,North America Sales,Europe Sales,Japan Sales,Other Sales,Global Sales,Critic Score,Critic Count,User Score,User Count,Developer,Rating",
        "mice":"Id,Manufacturer,Model,Resolution,Design,Number of Buttons,Interface,Weight,Size,Rating,Link Address" #Battery Type,Designed for,Extra Functions --- Size (L x W x H) in mm
    }
    json_ld_doc = json.dumps(data)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response

if __name__ == '__main__':
    app.run(host=host, port=port)