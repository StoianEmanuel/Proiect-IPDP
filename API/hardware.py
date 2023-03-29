from flask import Flask, request, jsonify
import sqlite3
import json
import os
from json import dumps

app = Flask(__name__)
#host = os.getenv('HOST', '127.0.0.1')
#port = int(os.getenv('PORT', '8086'))

# Function to establish connection with the database

def get_db_connection():
    conn = sqlite3.connect('../Data/gaming.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Retrieve all GPU from the database

def get_all_GPU(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GPU")
    rows = cursor.fetchall()
    cpu = []
    check_cols = [0,1,3,4,5,6,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    l = 0
    for row in rows:
        row_list = list(row)
        count = 0
        for i in check_cols:
            if not row_list[i] or row_list[i].upper() == 'NULL':
                row_list[i] = "N/A"
                count += 1
        if int(row_list[2]) < 1970:
            row_list[2] = "N/A"
            count += 1
    
        cp = {
            'Model': row_list[0],
	        'Manufacturer': row_list[1],
	        'Release Year': row_list[2],
            'Discontinued': row_list[3],
            'Graphics Processor': row_list[4],
            'Transistors': row_list[5],
            'Technology': row_list[6],
            'Shading Units': row_list[7],
            'Core Base Clock': row_list[8],
            'Core Boost Clock': row_list[9],
            'Memory Type': row_list[10],
            'Memory Size': row_list[11],
            'Memory Bandwidth': row_list[12],
            'Memory Clock Speed (Effective)': row_list[13],
            'TDP': row_list[14],
            'Display Outputs': row_list[15],
            'Cooling System': row_list[16],
            'Cooling Type': row_list[17],
            'DirectX': row_list[18],
            'OpenGL': row_list[19],
            'OpenCL': row_list[20],
            'Vulkan': row_list[21],
            'Shader Model': row_list[22],
            'CUDA': row_list[23]
        }

        if count < len(row_list)*3/10:
            if limit is None:
                cpu.append(cp)
            elif l < int(limit):
                cpu.append(cp)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return cpu


# Retrieve all CPU from the database

def get_all_CPU(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM CPU")
    rows = cursor.fetchall()
    cpu = []
    check_cols = [0,1,2,3,5,6,9,10,11,14,15,16,17,18]
    l = 0
    for row in rows:
        row_list = list(row)
        count = 0
        for i in check_cols:
            if not row_list[i] or row_list[i].upper() == 'NULL':
                row_list[i] = "N/A"
                count += 1
        if int(row_list[4]) < 1970:
            row_list[4] = "N/A"
            count += 1
        
        cp = {
            'Model': row_list[0],
	        'Manufacturer': row_list[1],
	        'Family': row_list[2],
            'Codename': row_list[3],
            'Release Year': row_list[4],
            'Discontinued': row_list[5],
            'Base Clock': row_list[6],
            'Boost Clock': row_list[7],
            'Sockets': row_list[8],
            'L1 Cache Size': row_list[9],
            'L2 Cache Size': row_list[10],
            'Technology': row_list[11],
            'Number of Cores': row_list[12],
            'Number of Threads': row_list[13],
            'TDP': row_list[14],
            'System Memory Type': row_list[15],
            'System Memory Frequency': row_list[16],
            'Instruction Set': row_list[17],
            'Maximum Operating Temperature': row_list[18]
        }

        if count < len(row_list)*3/10:
            if limit is None:
                cpu.append(cp)
            elif l < int(limit):
                cpu.append(cp)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return cpu


# Retrieve all games from the database

def get_all_games(limit=None):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videogames")
    rows = cursor.fetchall()
    games = []
    l = 0
    check_cols1 = [1,2,4,5]
    check_cols2 = [15,16]
    for row in rows:
        count = 0
        row_list = list(row)
        for i in check_cols1:
            if not row_list[i] or row_list[i].upper() == 'NULL':
                row_list[i] = "N/A"
                count += 1
        for i in check_cols2:
            if not row_list[i] or row_list[i].upper() == 'NULL' or row_list[i].upper() == 'N/A':
                row_list[i] = "N/A"
                count += 1
        
        if (not row_list[11] or float(row_list[11]) == 0.0) and (not row_list[12] or float(row_list[12]) == 0.0):
                row_list[11] = "N/A"
                row_list[12] = "N/A"
                count += 2

        if (not row_list[13] or float(row_list[13]) == 0.0) and (not row_list[14] or float(row_list[14]) == 0.0):
                row_list[13] = "N/A"
                row_list[14] = "N/A"
                count += 2

        if row_list[3].upper() == 'N/A' or (row_list[3] != "N/A" and not row_list[3].isnumeric()) or (row_list[3] != "N/A" and row_list[3].isnumeric() and int(row_list[3])<1970):
                row_list[i] = "N/A"
                count += 1
        
        # Query the platform_mapping table to get the full platform name
        platform = row_list[2]
        cursor.execute(f"SELECT console_platform FROM platform_mappings WHERE game_platform = '{platform}'")
        resultat = cursor.fetchone()
        if resultat:
            platform = list(resultat)

        row_list[2] = platform[0]
        game = {
            '@Id': row_list[0],
            'Name': row_list[1],
            'Platform': row_list[2],
            'Year of Release': row_list[3],
            'Genre': row_list[4],
            'Publisher': row_list[5],
            'North America Sales': row_list[6],
            'Europe Sales': row_list[7],
            'Japan Sales': row_list[8],
            'Other Sales': row_list[9],
            'Global Sales': row_list[10],
            'Critic Score': row_list[11],
            'Critic Count': row_list[12],
            'User Score': row_list[13],
            'User Count': row_list[14],
            'Developer': row_list[15],
            'Rating': row_list[16]
        }
        if count < len(row_list)*3/10:
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
    check_cols = [1,2,5]
    for row in rows:
        count = 0
        row_list=list(row)
        for i in check_cols:
            if not row_list[i] or row_list[i].upper() == 'NULL':
                row_list[i] = "N/A"
                count += 1

        if int(row_list[3]) < 1970:
                count += 1
        if int(row_list[4]) == 0:
                count += 1
        console = {
            '@Id': row_list[0],
            'Name': row_list[1],
            'Manufacturer': row_list[2],
            'Year of Release': row_list[3],
            'Sales': row_list[4],
            'Type': row_list[5],
            'Number of Exclusives': row_list[6],
            'Processing Unit Type': row_list[7],
	        'CPU Equivalent': row_list[8],
	        'CPU Frequency': row_list[9],
	        'GPU Equivalent': row_list[10],
	        'RAM Size': row_list[11],
	        'RAM Frequency': row_list[12]
        }
        if count < len(row_list)*3/10:
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
    check_cols = [1,2,3,4,6,8,10,11,12,13]
    for row in rows:
        count = 0
        row_list=list(row)
        for i in check_cols:
            if not row_list[i] or row_list[i].upper() == 'NULL':
                row_list[i] = "N/A"
                count += 1
    
        if not row[5]:
            count += 1
        elif row[5] and int(row[5]) < 3 or int(row[5]) > 20:
            count += 1
        
        if not row[7]:
            count += 1
        elif row[7] and int(row[7]) > 250:
            count += 1
            
        if not row[9]:
            count += 1
        elif row[9] and float(row[9]) > 5:
            count += 1

        mouse = {
            '@Id': row_list[0],
            'Manufacturer': row_list[1],
            'Model': row_list[2],
            'Resolution': row_list[3],
            'Design': row_list[4],
            'Number of Buttons': row_list[5],
            'Interface': row_list[6],
            'Weight': row_list[7],
            'Size (L x W x H)': row_list[8], #Size (L x W x H) in mm
            'Rating': row_list[9],
            'Link Address': row_list[10],
            'Battery Type': row_list[11],
            'Designed for': row_list[12],
            'Extra Functions': row_list[13] 
        }
        if count < len(row_list)*3/10:
            if limit is None:
                mice.append(mouse)
            elif l < int(limit):
                mice.append(mouse)
                l += 1
            elif l==int(limit):
                break
    conn.close()
    return mice


# Define the route to retrieve all games/consoles/mice/CPU

@app.route('/get_data', methods=['GET'])
def get_data():
    # Check if data_type is set to either games or consoles
    data_type = request.args.get('data_type')
    snippet = request.args.get('snippet')
     # Define the valid data types
    valid_data_types = ['mice', 'consoles', 'video_games', 'CPU', 'GPU']

    # Check if data_type is valid
    if data_type not in valid_data_types:
        error_response = {'error': 'Invalid data type'}
        return jsonify(error_response), 400

    # Check if snippet parameter is provided
    if not snippet:
        error_response = {'error': 'snippet parameter is missing'}
        return jsonify(error_response), 400

    # Check if snippet parameter is valid
    if snippet.lower() not in ['true', 'false']:
        error_response = {'error': 'snippet parameter does not exist'}
        return jsonify(error_response), 404
    
    if data_type == 'consoles':
        contextul = "SQLite/consoles"
        if snippet.lower() == 'true':   info = get_all_consoles(limit=20)           # Retrieve first 20 consoles  
        else:   info = get_all_consoles()   # Retrieve all consoles
            
    elif data_type == 'video_games':
        contextul = "SQLite/video_games"
        if snippet.lower() == 'true':   info = get_all_games(limit=20)              # Retrieve first 20 games    
        else:   info = get_all_games()      # Retrieve all games
            

    elif data_type == 'mice':
        contextul = "SQLite/mice"
        if snippet.lower() == 'true': info = get_all_mice(limit=20)                 # Retrieve first 20 mice
        else:   info = get_all_mice()       # Retrieve all mice
            
    elif data_type == 'CPU':
        contextul = "SQLite/CPU"
        if snippet.lower() == 'true':   info = get_all_CPU(limit=20)                # Retrieve first 20 cpu
        else:   info = get_all_CPU()        # Retrieve all cpu

    elif data_type == 'GPU':
        contextul = "SQLite/GPU"
        if snippet.lower() == 'true':   info = get_all_GPU(limit=20)                # Retrieve first 20 cpu
        else:   info = get_all_GPU()        # Retrieve all cpu

    context = {
            "@schema": contextul
        }
    data = {
            "@context": context,
            "@list": info
        }
    json_ld_doc = json.dumps(data, indent=4)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response 

def get_column_data(table_name):
    conn = sqlite3.connect('../Data/gaming.sqlite')
    # Define the SQL query to retrieve column names
    sql_query = f"PRAGMA table_info({table_name})"
    # Execute the query and retrieve the results
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    col_names = [result[1] for result in results]
    # Join the column names with commas and print the resulting string
    meta = (",".join(col_names))
    return meta


#Method to get meta for the database
@app.route('/get_meta')
def get_meta():
    table_name1 = 'videogames'
    table_name2 = 'consoles'
    table_name3 = 'mice'
    table_name4 = 'CPU'
    table_name5 = 'GPU'

    meta1 = get_column_data(table_name1)
    meta2 = get_column_data(table_name2)
    meta3 = get_column_data(table_name3)
    meta4 = get_column_data(table_name4)
    meta5 = get_column_data(table_name5)

    # Create JSON-LD document
    context = {
        "@schema": "SQLite"
    }
    data = {
        "@context": context,
        "video_games": meta1,
        "consoles": meta2,
        "mice": meta3,          #"mice":"Id,Manufacturer,Model,Resolution,Design,Number of Buttons,Interface,Weight,Size,Rating,Link Address", #Battery Type,Designed for,Extra Functions --- Size (L x W x H) in mm
        "CPU": meta4,
        "GPU": meta5
    }
    json_ld_doc = json.dumps(data, indent=4)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response

if __name__ == '__main__':
    print('Use the port selected (Port 5000 from the message bellow is autogenerated)')
    if os.environ.get('PORT') is not None:
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        app.run(debug=True, host='0.0.0.0')