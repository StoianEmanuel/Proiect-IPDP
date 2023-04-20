import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import sqlite3
import re
from itertools import chain

def extract_number_with_reg_expr(string):
    numeric_part = re.findall(r"\d+\.+\d+", string)
    if numeric_part:
        number = float(numeric_part[0])
    else:
        number = -1
    return number

# Functie care returneaza valoarea numerica a fiecarui element din lista
def get_numeric_value(element):
    letters = ['a', 'b', 'c']
    if element.endswith(" Ultimate"):
        return float(element.split(" ")[0]) + 1
    if element[-1] in letters:
        return extract_number_with_reg_expr(element) + (ord(element[-1]) - ord('a'))/10
    if element.startswith("N/A"):
        return -1
    if element.startswith("ES"):                   # daca elementul incepe cu "ES", luam partea numerica de dupa "ES "
        return float(element.split(" ")[1]) - 0.1  # scadem 0.1 pentru a plasa versiunile ES inaintea celor non-ES
    else:
        return float(element)

# Citirea datelor din fișierul SQLite
connection = sqlite3.connect('./Data/gaming.sqlite')
df = pd.read_sql_query('SELECT * FROM GPU WHERE [Release Year] > 1970 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0', connection)

Transform_col   = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP']
API_v2_col      = ['Shader Model', 'CUDA', 'OpenCL']
API_v1_col      = ['DirectX', 'OpenGL']
Int_col         = ['Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)']

for column in chain(Transform_col, API_v2_col, API_v1_col):
    # Fill empty values ("") with 0
    df[column].fillna("0", inplace=True)
    
    if any(column in cases for cases in (Transform_col)):
        numeric_value = df[column].str.extract('(\d+)').astype(float)   # Extract the numeric part
        size_unit  = df[column].str.extract('([a-zA-Z]+)')               # Extract the unit part                             
        size_in_gb = np.where(size_unit == 'MB', numeric_value / 1024, numeric_value) # Conversie din MB în GB unde este cazul
        df[column] = size_in_gb                                         # Transform string into numbers
    elif column in API_v2_col:
        df[column] = df[column].str.replace('N/A', '0', regex=True)   # Replace "N/A" with "0"
        df[column] = df[column].str.extract('(\d+)').astype(float)   # Extract the numeric part
    elif column in API_v1_col:
        unique_values = df[column].unique()                         # List of unique values in DataFrame df for DirectX and OpenCL
        ord_list = sorted(unique_values, key=get_numeric_value)     # List of unique values in DataFrame df for DirectX and OpenCL sorted
        priority = {value: index for index, value in enumerate(ord_list)}   # Define the priority (values) for each unique values
        df[column] = df[column].map(priority)                       # Change the original values from df[column] into priority values
        continue                                                    # Skip the code below


# Columns used for corelation
main_key = ['Launch Price ($)']
keys = Transform_col + API_v1_col + API_v2_col + Int_col

# Remove unused columns
coloane_de_sters = list(set(df.columns) - set(keys) - set(main_key))
df = df.drop(columns=coloane_de_sters)

# Find coeficients for corelation
correlation_coefficients = []
for key in keys:
    coefficient, _ = pearsonr(df[main_key].values.flatten(), df[key].values.flatten())
    correlation_coefficients.append(coefficient)

# Return values set for corelation
correlation_df = pd.DataFrame({'Feature': keys, 'Correlation Coefficient': correlation_coefficients})
correlation_df = correlation_df.sort_values(by='Correlation Coefficient', ascending=False)
print(correlation_df)