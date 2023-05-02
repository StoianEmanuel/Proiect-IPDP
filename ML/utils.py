import re
import sqlite3
import pandas as pd
from scipy.stats import pearsonr

# Read data from db as dataframe
def get_data(db_path, db_query):
    connection = sqlite3.connect(db_path)
    df = pd.read_sql_query(db_query, connection)
    return df


# Functie care extrage 
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
