from flask import Flask, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "8567"))


# Function to establish connection with the database
def get_db_connection():
    conn = sqlite3.connect("./Data/gaming.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

# Function to return a value or the dessired value if value returned by condition is true
def set_value_if(value, op, test_value, result):
    if value is None:
        return result
    if op == "==" and value == test_value:
        return result
    if op == "<" and value < test_value:
        return result
    if op == "<=" and value <= test_value:
        return result
    if op == ">" and value > test_value:
        return result
    if op == ">=" and value >= test_value:
        return result
    return value


# Function to test if value returned by a condition is true
def test_value(value, op, test_value):
    if value is None:
        return True
    if op == "==" and value == test_value:
        return True
    if op == "<" and value < test_value:
        return True
    if op == "<=" and value <= test_value:
        return True
    if op == ">" and value > test_value:
        return True
    if op == ">=" and value >= test_value:
        return True
    return False


# Function used to update data from list lst and allow testing for simple or double condition
def update(lst, filters):
    for filter in filters:
        poz1, op1, test_value1, result1 = filter[0:4]
        lst[poz1] = set_value_if(lst[poz1], op1, test_value1, result1)
          
        if len(filter) == 9:    # double condition
            poz2, op2, test_value2, result2, modify = filter[4:9]
            if modify == True:      # check if the second value can be modified
                lst[poz2] = set_value_if(lst[poz2], op2, test_value2, result2)

    return lst


# Function used to test if values from list lst fulfill contions from filters
def filter(lst, filters):
    count = 0
    length = len(lst)

    for filter in filters:
        if len(filter) == 4:
            poz1, op1, test_value1 = filter[0:3]
            if test_value(lst[poz1], op1, test_value1) == True:
                count += 1

        elif len(filter) == 9:  # double condition
            poz1, op1, test_value1 = filter[0:3]
            poz2, op2, test_value2 = filter[4:7]
            if test_value(lst[poz1], op1, test_value1) == True and test_value(lst[poz2], op2, test_value2) == True:
                count += 2

    return count < length * 0.3
    

# Retrieve all data of certain type
def get_all(datatype= '',  limit = None, apply_update = False, apply_filter = False, filter_conditions = None, extra_updates = None):
    conn = sqlite3.connect("./Data/gaming.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {datatype}")
    rows = cursor.fetchall()
    data = []
    l = 0
    for row in rows:
        row_list = list(row)
        filter_value: bool
        if apply_filter:
            filter_value = filter(row_list, filter_conditions)

            if not filter_value:
                continue
            row_list = update(row_list, filter_conditions)

        else:
            if apply_update:
                row_list = update(row_list, filter_conditions)
        
        # apply extra updates
        if extra_updates:
            for updates in extra_updates:
                index, op, test_value, value = updates[0:4]
                row_list[index] = set_value_if(row_list[index], op, test_value, value)

        values = {}
        length = len(row_list)
        for i in range(length):
            values[cursor.description[i][0]] = row_list[i]

        if limit is None:
            data.append(values)
        elif l < int(limit):
            data.append(values)
            l += 1
        elif l == int(limit):
            break
    cursor.close()
    conn.close()
    return data


# Function to remove the last (key, value) pair from the dictionary
def remove_last_property(data_list):
    for data in data_list:
        data.popitem()  
    return data_list


# Function to update data from a dictionary using querys
def update_data_with_query(data, query_set):
    conn = sqlite3.connect("./Data/gaming.sqlite")
    column_table1, desired_column, table, column_table2 = query_set[0:4]
    for element in data:
        cursor = conn.cursor()
        
        # Get the current value of the specified column for the element
        current_value = element[column_table1]
        # Construct the SELECT query using the specified table, column and value
        query_string = f"SELECT {desired_column} FROM {table} WHERE {column_table2} = ?"
        cursor.execute(query_string, (current_value,))
        query_result = cursor.fetchone()
        if query_result:
            # If the query returned a result, update the current value of the column for the element
            element[column_table1] = query_result[0]
        else:
            # If the query did not return a result, keep the current value of the column for the element
            element[column_table1] = current_value
        cursor.close()
    conn.close()
    return data


# Define the route to retrieve all games/consoles/mice/CPU
@app.route("/get_data", methods=["GET"])
def get_data():
    # Check if data_type is set to either games or consoles
    data_type = request.args.get("data_type")
    snippet = request.args.get("snippet")
    # Define the valid data types
    valid_data_types = ["mice", "consoles", "video_games", "CPU", "GPU"]

    # Check if data_type is valid
    if data_type not in valid_data_types:
        error_response = {"error": "Invalid data type"}
        return jsonify(error_response), 400

    # Check if snippet parameter is provided
    if not snippet:
        error_response = {"error": "snippet parameter is missing"}
        return jsonify(error_response), 400

    # Check if snippet parameter is valid
    if snippet not in ["true", "false"]:
        error_response = {"error": "snippet parameter does not exist"}
        return jsonify(error_response), 404

    if data_type == "consoles":
        contextul = "SQLite/consoles"
        filter_conditions = [      # define conditions
            [	1	, "==",	"NULL",	None 	],
            [	2	, "==",	"NULL",	None 	],
            [	3	, "<" ,	1970  ,	None 	],
            [	5	, "==",	"NULL", None    ],
            [	8	, "==",	"NULL",	None	],
            [	9	, "==",	"NULL",	None 	],
            [	11	, "==",	"NULL",	None 	],
            [	12	, "==",	"NULL",	None    ]
        ]

        extra_updates = [         # updates that does not count for integrity conditions
            [	10	, "==" , "NULL" , None ] 
        ]
        if snippet == "true":
            info = get_all(datatype= "consoles",  limit = 20, apply_update = True, apply_filter = True, filter_conditions = filter_conditions, extra_updates = extra_updates)  # Retrieve first 20 consoles
        else:
            info = get_all(datatype= "consoles",  limit = None, apply_update = True, apply_filter = True, filter_conditions = filter_conditions, extra_updates = extra_updates)  # Retrieve all consoles
        info = remove_last_property(info)

    elif data_type == "video_games":
        contextul = "SQLite/video_games"
        filter_conditions = [      # define conditions
            [	1	, "==",	"NULL",	None 	],
            [	2	, "==",	"NULL",	None 	],
            [	3	, "<" , 1970 ,	None 	],
            [	4	, "==", "NULL",	None 	],
            [	5	, "==", "NULL",	None 	],
            [	11	, "==",	0.0   ,	None    ,  12,  "==", 0.0 , None, True],
            [	13	, "==", 0.0   ,	None 	,  14,  "==", 0.0 , None, True],
            [	15	, "==",	"NULL",	None    ],
            [	16	, "==",	"NULL",	None 	]
        ]
        if snippet == "true":
            info = get_all(datatype= "videogames",  limit = 20, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 mice
        else:
            info = get_all(datatype= "videogames",  limit = None, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all mice

        query_set = ['Platform', 'console_platform', 'platform_mappings', 'game_platform']
        info = update_data_with_query(info, query_set)

    elif data_type == "mice":
        contextul = "SQLite/mice"
        filter_conditions = [      # define conditions
            [	1	, "==",	"NULL",	None 	],
            [	2	, "==",	"NULL",	None 	],
            [	3	, "==",	"NULL",	None 	],
            [	4	, "==", "NULL",	None 	],
            [	5	, "<" ,	3     ,	None    ,  5,  ">" , 20 , None, True],
            [	6	, "==",	0     ,	None 	],
            [	7	, ">" ,	250   ,	None 	,  7,  "==" , 0 , None, True],
            [	8	, "==",	"NULL",	None	],
            [	9	, ">" ,	5     ,	None 	],
            [	10	, "==",	"NULL",	None 	],
            [	11	, "==",	"NULL",	None 	],
            [	12	, "==",	"NULL",	None    ],
            [	13	, "==",	"NULL",	None 	]
        ]
        if snippet == "true":
            info = get_all(datatype= "mice",  limit = 20, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 mice
        else:
            info = get_all(datatype= "mice",  limit = None, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all mice


    elif data_type == "CPU":
        contextul = "SQLite/CPU"
        filter_conditions = [      # define conditions
            [	0	, "==",	"NULL",	None 	],
            [	1	, "==",	"NULL",	None 	],
            [	2	, "==",	"NULL",	None 	],
            [	3	, "==",	"NULL",	None 	],
            [	4	, "<" ,	1970  ,	None 	],
            [	5	, "==",	0     ,	None 	],
            [	6	, "==",	0     ,	None 	],
            [	7	, "==",	"NULL",	"-" 	],
            [	9	, "==",	"NULL",	"-" 	],
            [	10	, "==",	"NULL",	None 	],
            [	11	, "==",	0     ,	None 	],
            [	12	, "==",	0     ,	None    , 4 , "<" ,	2000 ,	None ,  False	],
            [	14	, "==",	"NULL",	None 	],
            [	15	, "==",	"NULL",	None 	],
            [	16	, "==",	"NULL",	None 	],
            [	17	, "==",	"NULL",	None 	],
            [	18	, "==",	"NULL",	None 	],
            [	19	, "==",	0     ,	None 	]
        ]
        if snippet == "true":
            info = get_all(datatype= "CPU",  limit = 20, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 CPU
        else:
            info = get_all(datatype= "CPU",  limit = None, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all CPU

    elif data_type == "GPU":
        contextul = "SQLite/GPU"
        filter_conditions = [
            [	0	, "==",	"NULL",	None 	],
            [	1	, "==",	"NULL",	None 	],
            [	2	, "<" ,	1970  ,	None 	],
            [	3	, "==",	"NULL",	None 	],
            [	4	, "==",	"NULL",	None 	],
            [	5	, "==",	0     ,	None 	],
            [	6	, "==",	0     ,	None 	],
            [	8	, "==",	"NULL",	None 	],
            [	9	, "==",	"NULL",	"-" 	],
            [	10	, "==",	"NULL",	None 	],
            [	11	, "==",	"NULL",	None 	],
            [	12	, "==",	"NULL",	None 	],
            [	13	, "==",	"NULL",	None 	],
            [	14	, "==",	"NULL",	None 	],
            [	15	, "==",	"NULL",	None 	],
            [	16	, "==",	"NULL",	None 	],
            [	17	, "==",	"NULL",	None 	],
            [	18	, "==",	"NULL",	None 	],
            [	19	, "==",	"NULL",	None 	],
            [	20	, "==",	"NULL",	None 	],
            [	21	, "==",	"NULL",	None 	],
            [	22	, "==",	"NULL",	None 	],
            [	23	, "==",	"NULL",	None 	],
            [	24	, "==",	0     ,	None 	]
        ]
        if snippet == "true":
            info = get_all(datatype= "GPU",  limit = 20, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 GPU
        else:
            info = get_all(datatype= "GPU",  limit = None, apply_update = True, apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all GPU

    context = {"@schema": contextul}
    data = {"@context": context, "@list": info}
    json_ld_doc = json.dumps(data, indent=4)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc, status=200, mimetype="application/ld+json"
    )
    return response


def get_column_data(table_name):
    conn = sqlite3.connect("./Data/gaming.sqlite")
    # Define the SQL query to retrieve column names
    sql_query = f"PRAGMA table_info({table_name})"
    # Execute the query and retrieve the results
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    col_names = [result[1] for result in results]
    # Join the column names with commas and print the resulting string
    meta = ",".join(col_names)
    conn.close()
    return meta


# Method to get meta for the database
@app.route("/get_meta")
def get_meta():
    table_name1 = "videogames"
    table_name2 = "consoles"
    table_name3 = "mice"
    table_name4 = "CPU"
    table_name5 = "GPU"

    meta1 = get_column_data(table_name1)
    meta2 = get_column_data(table_name2)
    meta3 = get_column_data(table_name3)
    meta4 = get_column_data(table_name4)
    meta5 = get_column_data(table_name5)

    last_comma_index = meta2.rfind(",")  # find index of last comma
    meta2 = meta2[:last_comma_index]  # slice string to get left part to remove the price 

    # Create JSON-LD document
    context = {"@schema": "SQLite"}
    data = {
        "@context": context,
        "video_games": meta1,
        "consoles": meta2,
        "mice": meta3,
        "CPU": meta4,
        "GPU": meta5,
    }
    json_ld_doc = json.dumps(data, indent=4)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc, status=200, mimetype="application/ld+json"
    )
    return response


if __name__ == "__main__":
    app.run(host=host, port=port, debug=True)
