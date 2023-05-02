import numpy as np
from itertools import chain
from utils import get_data, get_correlation, get_numeric_value


# Return dataframe from database; depends on keys
def get_df_from_db(db_path, db_query, main_key, other_keys = None, API_v2_col = None, API_v1_col = None):
    # Get data from db
    df = get_data(db_path = db_path, db_query = db_query)

    keys = other_keys + API_v1_col + API_v2_col + main_key # Format data

    for column in chain(keys):
        df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0
        if df[column].dtype == object:
            if any(column in cases for cases in (other_keys + main_key)):
                size_unit  = df[column].str.extract('([a-zA-Z]+)')                                      # Extract the unit part
                numeric_value = df[column].str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)   # Extract the numeric part
                if 'CLOCK' in column.upper() and 'MEMORY' not in column.upper():
                    numeric_value = np.where(size_unit == 'MHz', numeric_value / 1000, numeric_value) # Convert MHz values into GHz where is necessary
                elif 'SIZE' in column:
                    numeric_value = np.where(size_unit == 'MB', numeric_value / 1024, numeric_value)  # Convert MB values into GB where is necessary
                df[column] = numeric_value  # Transform string into numbers

            elif column in API_v2_col:
                df[column] = df[column].str.replace('N/A', '0', regex=True)   # Replace "N/A" with "0"
                df[column] = df[column].str.extract('(\d+)').astype(float)   # Extract the numeric part

            elif column in API_v1_col:
                unique_values = df[column].unique()                         # List of unique values in DataFrame df for DirectX and OpenCL
                ord_list = sorted(unique_values, key=get_numeric_value)     # List of unique values in DataFrame df for DirectX and OpenCL sorted
                priority = {value: index for index, value in enumerate(ord_list)}   # Define the priority (values) for each unique values
                df[column] = df[column].map(priority)                       # Change the original values from df[column] into priority values
                continue                                                    # Skip the code below

    for i in range(len(df['Core Boost Clock'])):     # if Boost Clock is null it will take value from Base Clock
        if df['Core Boost Clock'][i] == 0:
            df['Core Boost Clock'][i] = df['Core Base Clock'][i]

    df['TDP'] = df['TDP'].replace(0, float('nan'))   # Replace 0 with NaN
    mean_values = df['TDP'].mean(skipna=True)        # Mean value of TDP without values NaN
    df['TDP'] = df['TDP'].fillna(mean_values)        # Replace NaN cu mean value

    # Remove unused columns from dataframe
    coloane_de_sters = list(set(df.columns) - set(keys))
    df = df.drop(columns=coloane_de_sters)    
    return df


main_key= ['Memory Size']
other_keys = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'TDP', 'Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Launch Price ($)']
API_v1_col = ['DirectX', 'OpenGL']
API_v2_col = ['Shader Model', 'CUDA', 'OpenCL']
db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM GPU WHERE [Release Year] > 1970 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0'
df = get_df_from_db(db_path = db_path,                db_query = db_query,
               main_key = main_key,               other_keys = other_keys,
               API_v1_col = API_v1_col,               API_v2_col = API_v2_col  
               ) 

print(main_key[0]+':\n', get_correlation(df, main_key = main_key[0], keys = other_keys + API_v2_col + API_v1_col))