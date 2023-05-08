from itertools import chain
import math, re, sqlite3
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures


# Read data from db as dataframe
def get_data(db_path, db_query):
    connection = sqlite3.connect(db_path)
    df = pd.read_sql_query(db_query, connection)
    connection.close()
    return df


# Extract number with regular expression
def extract_number_with_reg_expr(string):
    numeric_part = re.findall(r"\d+\.+\d+", string)
    if numeric_part:
        number = float(numeric_part[0])
    else:
        number = -1
    return number


# Return numeric value from an element
def get_numeric_value(element):
    letters = ['a', 'b', 'c']
    if element.endswith(" Ultimate"):
        return float(element.split(" ")[0]) + 1
    if element[-1] in letters:
        return extract_number_with_reg_expr(element) + (ord(element[-1]) - ord('a'))/10
    if element.startswith("N/A"):
        return -1
    if element.startswith("ES"):                   # remove "ES " if element starts with "ES"
        return float(element.split(" ")[1]) - 0.1  # ES versions have a lowert value than non-ES
    else:
        return float(element)


# Calculate correlation
def get_correlation(df, main_key, keys):
    # Find coeficients for correlation
    correlation_coefficients = []
    for key in keys:
        coefficient, _ = pearsonr(df[main_key].values.flatten(), df[key].values.flatten())
        correlation_coefficients.append(coefficient)

    # Return values set for correlation formated
    correlation_df = pd.DataFrame({'Feature': keys, 'Correlation Coefficient': correlation_coefficients})
    correlation_df = correlation_df.sort_values(by='Correlation Coefficient', ascending=False)
    return correlation_df


# Get unit from string value
def get_size_unit(df: pd.DataFrame):
    size_unit = []
    pattern = re.compile('[a-zA-Z]+')
    for element in df.values:
        t = pattern.findall(element)
        size_unit.append(t)
    return size_unit


# Transform MHz or Hz into GHz values
def convert_unit_to_ghz(size_unit, numeric_value):
    if size_unit == 'MHz':
        numeric_value /= 1000
    elif size_unit == 'KHz':
        numeric_value /= 1000**2
    elif size_unit == 'Hz':
        numeric_value /= 1000**3
    return numeric_value


# Transform MB or KB or B into GB values
def convert_unit_to_gb(size_unit, numeric_value):
    if size_unit == 'MB':
        numeric_value /= 1024
    elif size_unit == 'KB':
        numeric_value /= 1024**2
    elif size_unit == 'B':
        numeric_value /= 1024**3
    return numeric_value


# Extract float from str
def test_and_update(column: str, values):
    size_units = get_size_unit(values)                                                      # Extract the unit part
    numeric_values = values.str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)[0]   # Extract the numeric part

    if ('CLOCK' in column.upper() or 'FREQUENCY' in column.upper()) and 'MEMORY' not in column.upper():
        converted_values = []
        for i in range(len(size_units)):
            if size_units[i]:  # check if size_units[i] contains elements
                converted_values.append(convert_unit_to_ghz(size_units[i][0], numeric_values[i]))
            else:
                converted_values.append(numeric_values[i])
        numeric_values = pd.DataFrame(converted_values, columns=[column])
    elif 'SIZE' in column.upper():
        converted_values = []
        for i in range(len(size_units)):
            if size_units[i]:  # check if size_units[i] contains elements
                converted_values.append(convert_unit_to_gb(size_units[i][0], numeric_values[i]))
            else:
                converted_values.append(numeric_values[i])
        numeric_values = pd.DataFrame(converted_values, columns=[column])

    values = numeric_values  # Transform string into numbers
    return values


# Return dataframe from database; depends on keys
def get_df(db_path, db_query, keys = None, API_v2_col = None, API_v1_col = None):
    # Get data from db
    df = get_data(db_path = db_path, db_query = db_query)

    all_keys = keys                             # Format data
    if API_v2_col != None:
        all_keys = all_keys + API_v2_col
    if API_v2_col != None:
        all_keys = all_keys + API_v1_col

    for column in chain(all_keys):
        df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0
        if df[column].dtype == object:
            if any(column in cases for cases in (keys)):
                for column in chain(keys):
                    df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0
                    if df[column].dtype == object:
                        df[column] = test_and_update(column, df[column])

            elif column in API_v2_col:
                df[column] = df[column].str.replace('N/A', '0', regex=True)   # Replace "N/A" with "0"
                df[column] = df[column].str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)   # Extract the numeric part

            elif column in API_v1_col:
                unique_values = df[column].unique()                         # List of unique values in DataFrame df for DirectX and OpenCL
                ord_list = sorted(unique_values, key=get_numeric_value)     # List of unique values in DataFrame df for DirectX and OpenCL sorted
                priority = {value: index for index, value in enumerate(ord_list)}   # Define the priority (values) for each unique values
                df[column] = df[column].map(priority)                       # Change the original values from df[column] into priority values
                continue                                                    # Skip the code below

    return df


# Remove unused columns from dataframe
def remove_columns(df, keys):
    coloane_de_sters = list(set(df.columns) - set(keys))
    df = df.drop(columns=coloane_de_sters) 
    return df


# Add values for '*Boost Clock' column in dataframe where value is missing
def add_boost(df: pd.DataFrame, modify_column: str):
    if 'BOOST CLOCK' in modify_column.upper():
        column = modify_column.replace('Boost', 'Base')
        if column in df.columns and not df[column].empty:
            for i in range(len(df[modify_column])):     # if Boost Clock is null it will take value from Base Clock
                if df[modify_column][i] == 0:
                    df[modify_column][i] = df[column][i]
    return df[modify_column]


# Fill with mean value where value is missing
def fill_with_mean(df: pd.DataFrame, column: str):
    copy = df[column].replace(0, float('nan'))   # Replace 0 with NaN
    mean_values = copy.mean(skipna=True)        # Mean value of TDP without values NaN
    copy = copy.fillna(mean_values)        # Replace NaN cu mean value
    return copy


# Return Score for an element that is stored as a dataframe
def score_df(df, columns_reverse):                  
    score = 0
    for column in df.columns:
        if column in columns_reverse:
            score = score + math.log10(1/df[column] + 10)
        else:
            score = score + math.log10(df[column] + 10)
        
    return score


def get_scores(df, scalable_columns, scalable_columns_rev = None):
    # Initialize a MinMaxScaler
    scaler = MinMaxScaler()

    # Scale data and keep columns name
    scaled_values = scaler.fit_transform(df[scalable_columns])
    column_names = df[scalable_columns].columns.tolist()

    # Build new dataframe with the new data and name
    df_scaled = pd.DataFrame(scaled_values, columns=column_names)
    for column in scalable_columns:
        df_scaled[column] = np.log10(df[column] + 10)
    for column in scalable_columns_rev:
        df_scaled[column] = np.log10(1/df[column] + 10)
    
    #print(df_scaled.product(axis=1).values, '\n\n')
    #print(df_scaled.sum(axis=1).values)

    return(df_scaled.product(axis=1).values)


# Return Dataframe for predictions, liniar or polynomial regressor are optional
def predicition(release_year, linear_regressor = None, poly_regressor = None, degree = 2, columns = None, lin_int_col = None, poly_int_col = None):
    X_release_year = np.array(release_year).reshape(-1, 1)
    concatenated_matrix = X_release_year

    if linear_regressor is not None:
        linear_prediction = linear_regressor.predict(X_release_year)
        linear_prediction = np.exp(linear_prediction)
        if lin_int_col is not None:     # if lin_int_col is used change float values for columns into int type
            linear_prediction[:, lin_int_col] = linear_prediction[:, lin_int_col].astype(int)
        concatenated_matrix = np.concatenate((concatenated_matrix, linear_prediction), axis=1)


    if poly_regressor is not None:
        poly_features = PolynomialFeatures(degree=degree)
        X_release_year_poly = poly_features.fit_transform(X_release_year)

        poly_prediction = poly_regressor.predict(X_release_year_poly)
        poly_prediction = np.exp(poly_prediction)
        if poly_int_col is not None:    # if poly_int_col is used change float values for columns into int type
            poly_prediction[:, poly_int_col] = poly_prediction[:, poly_int_col].astype(int)
        concatenated_matrix = np.concatenate((concatenated_matrix, poly_prediction), axis=1)


    if linear_regressor is None and poly_regressor is None:
        return pd.DataFrame()

    df = pd.DataFrame(concatenated_matrix, columns=columns)
    return df


# Return similarity coefficient between 2 strings
def jaccard_similarity(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union
    return similarity * 100


def get_row_for_score(df, score):

    return df