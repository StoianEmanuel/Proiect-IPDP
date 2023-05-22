from flask import Flask, request, jsonify
import sqlite3, json, os
import sys
sys.path.insert(0, '../ML')
from utils import add_size_units_to_df_values, remove_columns, reorder_columns
from consoles_predictions import ConsolePredictor
from predictions import Processor
from delete_methods import delete_item_by_model_and_manufacturer, delete_item_by_id
from meta_method import get_meta_data

app = Flask(__name__)
# host = os.getenv('HOST', '127.0.0.1')
# port = int(os.getenv('PORT', '8086'))


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


# Function used to test if values from list lst fulfill contions from filters
def filter(lst, filters):
    count = 0
    length = len(lst)

    for filter in filters:
        if len(filter) >= 4:
            poz1, op1, test_value1, result1 = filter[0:4]
            first_cond_val  = test_value(lst[poz1], op1, test_value1)

            if len(filter) == 9:
                poz2, op2, test_value2, result2, modify = filter[4:9]
                second_cond_val = test_value(lst[poz2], op2, test_value2)
                if first_cond_val and second_cond_val:
                    count += 2
                if modify and second_cond_val:
                    lst[poz2] = result2
                continue

            if first_cond_val:
                lst[poz1] = result1
                count += 1

    return count < length * 0.3, lst
    

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
    
        if apply_filter or (not apply_filter and apply_update):
            filter_value, values = filter(row_list, filter_conditions)

            if not filter_value:
                continue

            row_list = values
        
        # apply extra updates
        if extra_updates:
            for updates in extra_updates:
                index, op, test_value, value = updates[0:4]
                filter_value, v = filter([row_list[index]], [[updates]])

                if filter_value:
                    row_list[index] = value

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
def remove_columns(data_list, columns_to_remove):
    for data in data_list:
        for column in columns_to_remove:
            data.pop(column, None)  
    return data_list


# Function to update data from a dictionary using querys
def update_data_using_query(data, query_set):
    conn = sqlite3.connect("../Data/gaming.sqlite")
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
            info = get_all(datatype= "consoles",  limit = 20, apply_update = True, apply_filter = True,
                            filter_conditions = filter_conditions, extra_updates = extra_updates)  # Retrieve first 20 consoles
        else:
            info = get_all(datatype= "consoles",  limit = None, apply_update = True, apply_filter = True,
                            filter_conditions = filter_conditions, extra_updates = extra_updates)  # Retrieve all consoles
        
        columns_to_remove = ['Launch Price ($)']
        info = remove_columns(info, columns_to_remove)


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
            info = get_all(datatype= "videogames",  limit = 20, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 mice
        else:
            info = get_all(datatype= "videogames",  limit = None, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all mice

        query_set = ['Platform', 'console_platform', 'platform_mappings', 'game_platform']
        info = update_data_using_query(info, query_set)

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
            info = get_all(datatype= "mice",  limit = 20, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 mice
        else:
            info = get_all(datatype= "mice",  limit = None, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all mice


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
            info = get_all(datatype= "CPU",  limit = 20, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve first 20 CPU
        else:
            info = get_all(datatype= "CPU",  limit = None, apply_update = True,
                            apply_filter = True, filter_conditions = filter_conditions)  # Retrieve all CPU

    else:
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
            info = get_all(datatype= "GPU",  limit = 20, apply_update = True, apply_filter = True,
                            filter_conditions = filter_conditions)  # Retrieve first 20 GPU
        else:
            info = get_all(datatype= "GPU",  limit = None, apply_update = True, apply_filter = True,
                            filter_conditions = filter_conditions)  # Retrieve all GPU
        columns_to_remove = ['Integration Density']
        info = remove_columns(info, columns_to_remove)


    # Return response in JSON-LD format
    context = {"@schema": contextul}
    data = {"@context": context, "@list": info}
    json_ld_doc = json.dumps(data, indent=4)

    response = app.response_class(
        response=json_ld_doc, status=200, mimetype="application/ld+json"
    )
    return response


# Method to get meta for the database
@app.route("/get_meta", methods = ['GET'])
def get_meta():
    response = get_meta_data("../Data/gaming.sqlite")
    return response


# Method to filter and sort year values used for predictions
def get_years_for_predictions(years_list, min_value = 1975, max_value = 2030):
    years_int = []
    for number in years_list:
        n = int(number)
        if min_value <= n <= max_value:
            years_int.append(n)

    years_int = sorted(set(years_int))
    years_int = list(years_int)
    return years_int


# Define the route to retrieve predictions for consoles/CPU/GPU
@app.route("/get_prediction")
def get_data_for_ML():

    data_type = request.args.get("data_type")
    valid_data_types = ["consoles", "CPU", "GPU"]
    years = request.args.get("years")

    # Check if data_type is valid
    if data_type not in valid_data_types:
        error_response = {"error": "Invalid data type"}
        return jsonify(error_response), 400

    # Check if years parameter is provided
    if not years:
        error_response = {"error": "years parameter is missing"}
        return jsonify(error_response), 400
    
    numbers = years.split(',')

    if data_type == "consoles":
        contextul = "SQLite/consoles"
        years_int = get_years_for_predictions(years_list=numbers, min_value=1985, max_value=2030)

        consoles = ConsolePredictor(database_path = '../Data/gaming.sqlite', linear_regressor_path='../ML/consoles_linear_regressor.joblib',
                 polynomial_regressor_path1='../ML/consoles_poly_regressor1.joblib', poly_degree1=2,
                 polynomial_regressor_path2='../ML/consoles_poly_regressor2.joblib', poly_degree2=7)
        
        consoles.set_data_for_df()
        consoles.prediction_for_consoles(years = years_int)

        consoles.add_units_for_prediction_df('predicted')
        df = consoles.predicted_df
 
        df = reorder_columns(df, [0, 6, 7, 4, 1, 5, 2, 3, 8])

        info = df.to_dict(orient='records')

    elif data_type == "GPU":
        contextul = "SQLite/GPU"
        years_int = get_years_for_predictions(years_list=numbers, min_value=1990, max_value=2030)

        gpu_processor = Processor( year = years_int,
                    linear_regressor_file = '../ML/GPU_linear_regressor.joblib',
                    lin_int_col  = [0, 2],

                    poly_regressor_file1 = '../ML/GPU_poly_regressor.joblib',
                    poly_int_col1 = [1, 2, 3],
                    degree1 = 2,
                    
                    columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 
                                'Core Boost Clock', 'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units',
                                'Memory Clock Speed (Effective)', 'Launch Price ($)'],
                    
                    db_path = '../Data/gaming.sqlite',
                    db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1989 AND [Transistors (millions)] > 0 AND [Integration Density] 
                    IS NOT NULL AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND 
                    [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [TDP] IS NOT NULL AND [Launch Price ($)] > 0''',

                    string_columns = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 
                                      'Memory Size', 'TDP', 'Integration Density'])
        
        gpu_processor.read_data()

        df = gpu_processor.predicted_df
        df = reorder_columns(df, [0, 1, 2, 8, 7, 4, 5, 9, 6, 10, 3, 11])    # fara 8

        columns_to_update = ['TDP', 'Core Base Clock', 'Core Boost Clock', 'Memory Bandwidth', 'Memory Size', 
                             'Integration Density', 'Memory Clock Speed (Effective)']
        df = add_size_units_to_df_values(df, columns_to_update)
        for column in df.columns:
            if column not in columns_to_update:
                df[column] = df[column].astype(int)

        info = df.to_dict(orient='records')

    else:
        contextul = "SQLite/CPU"
        years_int = get_years_for_predictions(years_list=numbers, min_value=1975, max_value=2030)
        
        cpu_processor = Processor(
                year = years_int,
                linear_regressor_file = '../ML/CPU_linear_regressor.joblib',
                lin_int_col = [0, 1],

                poly_regressor_file1 = '../ML/CPU_poly_regressor.joblib',
                poly_int_col1 = [0, 1, 2, 3],
                degree1 = 10,
                
                columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                    'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'],
                
                db_path = '../Data/gaming.sqlite',
                db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND
                                [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND
                                [Launch Price ($)] > 0 AND [Maximum Operating Temperature] IS NOT NULL AND [TDP] IS NOT NULL''',

                string_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
                'System Memory Frequency', 'TDP'])
        
        cpu_processor.read_data()

        df = cpu_processor.predicted_df
        df = reorder_columns(df, [0, 1, 8, 9, 3, 4, 5, 6, 10, 2, 7, 11])

        df = add_size_units_to_df_values(df, columns = ['TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                    'Maximum Operating Temperature', 'System Memory Frequency'])
        
        columns_to_update = ['TDP', 'Base Clock', 'Boost Clock','L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
                'System Memory Frequency', 'TDP']
        for column in df.columns:
            if column not in columns_to_update:
                df[column] = df[column].astype(int)
        info = df.to_dict(orient='records')


    # Return response in JSON-LD format
    context = {"@schema": contextul}
    data = {"@context": context, "@list": info}
    json_ld_doc = json.dumps(data, indent=4)

    response = app.response_class(
        response=json_ld_doc, status=200, mimetype="application/ld+json"
    )
    return response


# Define the route to delete items from mice/consoles/video_games tables
@app.route('/delete_item_by_id', methods=['DELETE'])
def delete_item_using_id():
    response, status_code = delete_item_by_id()
    return response, status_code


# Define the route to delete items from CPU/GPU tables
@app.route('/delete_item', methods=['DELETE'])
def delete_item_using_model_and_manufacturer_():
    response, status_code = delete_item_by_model_and_manufacturer()
    return response, status_code


if __name__ == "__main__":
    print("Use the port selected (Port 5000 from the message bellow is autogenerated)")
    if os.environ.get("PORT") is not None:
        app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT"))
    else:
        app.run(debug=True, host="0.0.0.0")
