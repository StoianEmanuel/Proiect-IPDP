import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sqlite3
from itertools import chain
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump

# Read data from db
def get_data(db_path, db_query):
    connection = sqlite3.connect(db_path)
    df = pd.read_sql_query(db_query, connection)
    return df

# Change content of columns of dataframe where the values are string
def update_values(df, Transform_col):
    for column in chain(Transform_col):
        df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0

        if any(column in cases for cases in (Transform_col)):
            numeric_value = df[column].str.extract('(\d+\.\d+|\d+\.\d*|\.\d+|\d+)').astype(float)   # Extract the numeric part
            size_unit  = df[column].str.extract('([a-zA-Z]+)')                                      # Extract the unit part
            if 'CLOCK' in column.upper() and 'MEMORY' not in column.upper():
                numeric_value = np.where(size_unit == 'MHz', numeric_value / 1000, numeric_value) # Convert MHz values into GHz where is necessary
            elif 'SIZE' in column.upper():                       
                numeric_value = np.where(size_unit == 'MB', numeric_value / 1024, numeric_value)  # Convert MB values into GB where is necessary
             
            df[column] = numeric_value  # Transform string into numbers


db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM GPU WHERE [Release Year] > 1985 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0'
df = get_data(db_path, db_query)

# Define set of columns from db of string or integer values
Transform_col   = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP']
Int_col         = ['Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Launch Price ($)']

update_values(df, Transform_col)

# Remove unused columns
keys = Transform_col + Int_col
coloane_de_sters = list(set(df.columns) - set(keys))
df = df.drop(columns=coloane_de_sters)

for i in range(len(df['Core Boost Clock'])):     # if Core Boost Clock is null it will take value from Core Base Clock
    if df['Core Boost Clock'][i] == 0:
        df['Core Boost Clock'][i] = df['Core Base Clock'][i]

df['Shading Units ln'] = df['Shading Units'].replace(0, 1)
df['Shading Units ln'] = np.log(df['Shading Units ln'])

df['TDP ln'] = df['TDP'].replace(0, float('nan'))   # Replace 0 with NaN
mean_values = df['TDP ln'].mean(skipna=True)        # Mean value of TDP without values NaN
df['TDP ln'] = df['TDP ln'].fillna(mean_values)     # Replace NaN cu mean value
df['TDP ln'] = np.log(df['TDP ln'])                 # Transform data into ln(data)

keys = [col for col in keys if col != 'Release Year' and col != 'TDP' and col != 'Shading Units']
for column in keys:
    df[column + ' ln'] = np.log(df[column])         # Create new column in dataframe and transform data into ln(data)

X  = df[['Release Year']].values
y_liniar  = df[['Transistors (millions) ln', 'Process Size (nm) ln', 'TDP ln', 'Core Base Clock ln', 'Core Boost Clock ln', 'Memory Bandwidth ln']].values
y_poly = df[['Shading Units ln', 'Memory Size ln', 'Memory Clock Speed (Effective) ln', 'Launch Price ($) ln']].values

# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 2)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Liniar regression for the rest of the columns
liniar_regressor = LinearRegression()
liniar_regressor.fit(X, y_liniar)

# Save liniar regression model and polynomial regression model
dump(liniar_regressor, './ML/GPU_liniar_regressor.joblib')
dump(poly_regressor, './ML/GPU_poly_regressor.joblib')