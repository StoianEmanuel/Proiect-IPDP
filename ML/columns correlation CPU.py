import numpy as np
from itertools import chain
from utils import get_data, get_correlation


# Return dataframe from database; depends on keys
def get_df_from_db(db_path, db_query, main_key, other_keys = None):
    # Get data from db
    df = get_data(db_path = db_path, db_query = db_query)

    keys = other_keys + main_key # Format data

    for column in chain(keys):
        df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0
        if df[column].dtype == object:
            if any(column in cases for cases in (other_keys + main_key)):
                size_unit  = df[column].str.extract('([a-zA-Z]+)')                                      # Extract the unit part
                numeric_value = df[column].str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)   # Extract the numeric part
                if 'CLOCK' in column.upper() and 'MEMORY' not in column.upper():
                    numeric_value = np.where(size_unit == 'MHz', numeric_value / 1000, numeric_value) # Convert MHz values into GHz where is necessary
                elif 'SIZE' in column:
                    numeric_value = np.where(size_unit == 'KB', numeric_value / 1024, numeric_value)  # Convert MB values into GB where is necessary
                df[column] = numeric_value  # Transform string into numbers
        
    # Remove unused columns from dataframe
    coloane_de_sters = list(set(df.columns) - set(keys))
    df = df.drop(columns=coloane_de_sters)    
    return df

main_key= ['Release Year']
other_keys = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 'System Memory Frequency', 'TDP', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']
db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0'
df = get_df_from_db(db_path = db_path,                db_query = db_query,
               main_key = main_key,               other_keys = other_keys,
               ) 

print(main_key[0]+':\n', get_correlation(df, main_key = main_key[0], keys = other_keys))