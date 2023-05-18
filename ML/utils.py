from itertools import chain
import math
import re, sqlite3
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
    pattern = re.compile('[a-zA-Z]+(?:/mm\^2)?')
    for element in df.values:
        t = pattern.findall(element)
        size_unit.append(t)
    return size_unit


# Transform K/mm^2 into M/mm^2 values
def convert_unit_to_M_per_mm_sq(size_unit, numeric_value):
    if size_unit == 'K/mm^2':
        numeric_value /= 1000
    return numeric_value


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


def integer_or_float_value(value):
    str_value = str(value)
    decimal_index = str_value.find('.')
    
    if decimal_index != -1 and decimal_index + 2 < len(str_value):
        value = float(str_value[:decimal_index + 2])
    
    return value


def value_to_memory_size_unit(value):
    nr = 0
    while value < 1:
        if value == 0:
            return ''
        value *= 1024
        nr += 1

    value = integer_or_float_value(value)
    if nr == 0:
        value = str(value) + ' GB'
    elif nr == 1:
        value = str(value) + ' MB'
    elif nr == 2:
        value = str(value) + ' KB'
    else:
        value = str(value) + ' B'
    
    return value


def value_to_clock_speed_unit(value):
    nr = 0
    while value < 1:
        if value == 0:
            return ''
        value *= 1000
        nr += 1

    value = integer_or_float_value(value)
    if nr == 0:
        value = str(value) + ' GHz'
    elif nr == 1:
        value = str(value) + ' MHz'
    elif nr == 2:
        value = str(value) + ' KHz'
    else:
        value = str(value) + ' Hz'

    return value


def add_string_unit(value, unit):       # W sau GB/S sau C sau MHz
    if value == 0:
        return ''
    return str(integer_or_float_value(value)) + ' ' + unit


def value_to_density_unit(value):
    nr = 0
    while value < 1:
        if value == 0:
            return ''
        value *= 1000
        nr += 1

    value = integer_or_float_value(value)
    if nr == 0:
        value = str(value) + ' M/mm^2'
    else:
        value = str(value) + ' K/mm^2'

    return value
     

def value_to_memory_speed_unit(value):
    nr = 0
    while value < 1:
        if value == 0:
            return ''
        value *= 1000
        nr += 1
    
    value = integer_or_float_value(value)
    if nr == 0:
        value = str(value) + ' MHz'
    elif nr == 1:
        value = str(value) + ' KHz'
    else:
        value = str(value) + ' Hz'

    return value


def add_size_units_to_df_values(df: pd.DataFrame, columns):
    for column in columns:
        if ('CLOCK' in column.upper() or 'FREQUENCY' in column.upper()) and 'MEMORY' not in column.upper() and 'RAM' not in column:
            df[column] = df[column].apply(value_to_clock_speed_unit)
        elif 'SIZE' in column.upper():
            df[column] = df[column].apply(value_to_memory_size_unit)
        elif 'MEMORY' in column.upper() or 'RAM' in column and ('FREQUENCY' in column.upper() or 'SPEED' in column.upper()):
            df[column] = df[column].apply(value_to_memory_speed_unit)
        elif 'DENSITY' in column.upper():
            df[column] = df[column].apply(value_to_density_unit)
        elif 'BANDWIDTH' in column.upper():
            df[column] = df[column].apply(lambda x: add_string_unit(x, 'GB/s'))
        elif 'TEMPERATURE' in column.upper():
            df[column] = df[column].apply(lambda x: add_string_unit(x, 'C'))
        elif 'TDP' in column.upper():
            df[column] = df[column].apply(lambda x: add_string_unit(x, 'W'))

    return df


# Extract float from str
def test_and_update(column: str, values):
    size_units = get_size_unit(values)                                                      # Extract unit part
    numeric_values = values.str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)[0]   # Extract numeric part

    # if + elif to format data for some columns
    if ('CLOCK' in column.upper() or 'FREQUENCY' in column.upper()) and 'MEMORY' not in column.upper():
        converted_values = []
        for i in range(len(size_units)):
            if size_units[i]:
                converted_values.append(convert_unit_to_ghz(size_units[i][0], numeric_values[i]))
            else:
                converted_values.append(numeric_values[i])
        numeric_values = pd.DataFrame(converted_values, columns=[column])
    
    elif 'SIZE' in column.upper():
        converted_values = []
        for i in range(len(size_units)):
            if size_units[i]:
                converted_values.append(convert_unit_to_gb(size_units[i][0], numeric_values[i]))
            else:
                converted_values.append(numeric_values[i])
        numeric_values = pd.DataFrame(converted_values, columns=[column])

    elif 'DENSITY' in column.upper():
        converted_values = []
        for i in range(len(size_units)):
            if size_units[i]:
                converted_values.append(convert_unit_to_M_per_mm_sq(size_units[i][0], numeric_values[i]))
            else:
                converted_values.append(numeric_values[i])
        numeric_values = pd.DataFrame(converted_values, columns=[column])

    values = numeric_values  # Transform string into numbers
    return values


# Return dataframe from database; depends on keys
def get_df(db_path, db_query, keys = None, API_v2_col = None, API_v1_col = None):
    # Get data from db
    df = get_data(db_path = db_path, db_query = db_query)

    all_keys = keys
    if API_v2_col != None:
        all_keys = all_keys + API_v2_col
    if API_v2_col != None:
        all_keys = all_keys + API_v1_col

    for column in chain(all_keys):
        df[column].fillna("0", inplace=True)    # Replace NaN with 0
        if df[column].dtype == object:          # if column is different than float, int
            if any(column in cases for cases in (keys)):
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
    drop_columns = list(set(df.columns) - set(keys))
    df = df.drop(columns=drop_columns) 
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
def fill_with_mean_column(df: pd.DataFrame, column: str):
    copy = df[column].replace(0, float('nan'))   # Replace 0 with NaN for an easier way of ignoring 0 values when calculating mean value
    mean_value = copy.mean(skipna=True)        # Mean value of TDP without values NaN
    copy = copy.fillna(mean_value)        # Replace NaN cu mean value
    return copy


# Return DataFrame after the content of rows is filtered based on condsitions provided as argument
def filter_values(df: pd.DataFrame, conditions = []):
    if not conditions:
        return df

    for condition in conditions:
        column, operator, test_values = condition[0:3]
        if operator == '==':
            df = df[df[column].isin(test_values)]
        elif operator == '<':
            df = df[df[column] < min(test_values)]   
        elif operator == '>':
            df = df[df[column] > max(test_values)]
        elif operator == '!=':
            df = df[~df[column].isin(test_values)]
            
    return df


# Check if values provided is 0, None, null or Nan
def is_zero_none_null_nan(var):
    if isinstance(var, str):
        return False
    elif isinstance(var, (int, float)):
        if var == 0 or pd.isnull(var) or math.isnan(var):
            return True
    elif var is None:
        return True
    return False


# Return a column from a Dataframe where 0 values are replaced with mean_value of that column 
def fill_column_with_mean_value(df: pd.DataFrame, column: str, interval_columns = [], cases = []):  # conditions are stored in a list and sent as an argument
    # conditions = [ [ column_filter, operator, [values_to_compare] ], ... ]
    # cases = [ column, [values] ]
    n = len(df[column].values)
    df_copy = df
    for index in range(0, n):
        value = df_copy.iloc[index]
        aux = df

        if is_zero_none_null_nan(value[column]):
            if interval_columns:
                for column_case in interval_columns:
                    aux_copy = filter_values(aux, [[column_case, '<', [value[column_case] + 10]]])
                    aux_copy = filter_values(aux_copy, [[column_case, '>', [value[column_case] - 10]]])

                    if not aux_copy.empty:
                        aux = aux_copy
                    else:
                        break
        
            if cases:
                for column_case, values in cases:
                    copy_aux = []
                    for v in values:
                        if v == value[column_case]:
                            copy_aux = filter_values(aux, [[column_case, '==', values]])
                            break

                    if len(copy_aux) > 0:
                        aux = copy_aux

            aux = aux[column].replace(0, float('nan'))
            mean_value = aux.mean(skipna=True)
            df_copy.loc[index, column] = mean_value

    return df_copy


# Return a DataFrame column that contains scores for items
def get_scores(df, scalable_columns, scalable_columns_rev = None):
    # Initialize MinMaxScaler
    scaler = MinMaxScaler()

    # Scale data and keep columns name
    scaled_values = scaler.fit_transform(df[scalable_columns])
    column_names = df[scalable_columns].columns.tolist()
    df_scaled = pd.DataFrame(scaled_values, columns=column_names)

    # log10(value + 10) if value is 0 => log10(10) = 1, otherwise = -inf
    for column in scalable_columns:
        df_scaled[column] = np.log10(df[column] + 10)
    if scalable_columns_rev:
        for column in scalable_columns_rev:
            df_scaled[column] = np.log10(1/df[column] + 10)

    return df_scaled.product(axis=1).values


# Return Dataframe for predictions, liniar or polynomial regressor are optional
def predicition(release_year, columns = None, linear_regressor = None, lin_int_col = None, poly_regressor1 = None, poly_degree1 = 2,
                 poly_int_col1 = None, poly_regressor2 = None, poly_degree2 = 2, poly_int_col2 = None):
    X_release_year = np.array(release_year).reshape(-1, 1)
    concatenated_matrix = X_release_year

    if linear_regressor is not None:
        linear_prediction = linear_regressor.predict(X_release_year)
        linear_prediction = np.exp(linear_prediction)
        if lin_int_col is not None:     # if lin_int_col is used change float values for columns into int type
            linear_prediction[:, lin_int_col] = linear_prediction[:, lin_int_col].astype(int)
        concatenated_matrix = np.concatenate((concatenated_matrix, linear_prediction), axis=1)

    if poly_regressor1 is not None:
        poly_features = PolynomialFeatures(degree=poly_degree1)
        X_release_year_poly = poly_features.fit_transform(X_release_year)

        poly_prediction = poly_regressor1.predict(X_release_year_poly)
        poly_prediction = np.exp(poly_prediction)
        if poly_int_col1 is not None:    # if poly_int_col is used change float values for columns into int type
            poly_prediction[:, poly_int_col1] = poly_prediction[:, poly_int_col1].astype(int)
        concatenated_matrix = np.concatenate((concatenated_matrix, poly_prediction), axis=1)

    if poly_regressor2 is not None:
        poly_features = PolynomialFeatures(degree=poly_degree2)
        X_release_year_poly = poly_features.fit_transform(X_release_year)

        poly_prediction = poly_regressor2.predict(X_release_year_poly)
        poly_prediction = np.exp(poly_prediction)
        if poly_int_col2 is not None:    # if poly_int_col is used change float values for columns into int type
            poly_prediction[:, poly_int_col2] = poly_prediction[:, poly_int_col2].astype(int)
        concatenated_matrix = np.concatenate((concatenated_matrix, poly_prediction), axis=1)

    if linear_regressor is None and poly_regressor1 is None:
        return pd.DataFrame()

    df = pd.DataFrame(concatenated_matrix, columns=columns)
    return df


# Return similarity coefficient between 2 strings as %
def jaccard_similarity(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union
    return similarity * 100


# Return DataFrame with columns in the specified order 
def reorder_columns(df, new_order):
    return df.iloc[:, new_order]