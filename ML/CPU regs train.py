import numpy as np
from sklearn.linear_model import LinearRegression
from utils import get_data
from itertools import chain
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump


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
                numeric_value = np.where(size_unit == 'KB', numeric_value / 1024, numeric_value)  # Convert KB values into MB where is necessary
             
            df[column] = numeric_value  # Transform string into numbers


db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0'
df = get_data(db_path, db_query)

# Define set of columns from db of string or integer values
Transform_col   = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 'System Memory Frequency', 'TDP']
Int_col         = ['Release Year', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']

update_values(df, Transform_col)

# Remove unused columns
keys = Transform_col + Int_col
coloane_de_sters = list(set(df.columns) - set(keys))
df = df.drop(columns=coloane_de_sters)

for i in range(len(df['Boost Clock'])):     # if Boost Clock is null it will take value from Core Base Clock
    if df['Boost Clock'][i] == 0:
        df['Boost Clock'][i] = df['Base Clock'][i]

df['Number of Threads ln'] = df['Number of Threads'].replace(0, 0.5)
df['Number of Threads ln'] = np.log(df['Number of Threads ln'])

df['L2 Cache Size ln'] = df['L2 Cache Size'].replace(0, 0.001)
df['L2 Cache Size ln'] = np.log(df['L2 Cache Size ln'])

df['TDP'] = df['TDP'].replace(0, float('nan'))   # Replace 0 with NaN
mean_values = df['TDP'].mean(skipna=True)        # Mean value of TDP without values NaN
df['TDP'] = df['TDP'].fillna(mean_values)        # Replace NaN cu mean value
df['TDP ln'] = np.log(df['TDP'])                 # Transform data into ln(data)

df['Maximum Operating Temperature'] = df['Maximum Operating Temperature'].replace(0, float('nan'))   # Replace 0 with NaN
mean_values = df['Maximum Operating Temperature'].mean(skipna=True)        # Mean value of TDP without values NaN
df['Maximum Operating Temperature'] = df['Maximum Operating Temperature'].fillna(mean_values)        # Replace NaN cu mean value
df['Maximum Operating Temperature ln'] = np.log(df['Maximum Operating Temperature'])                 # Transform data into ln(data)

keys = [col for col in keys if col != 'Release Year' and col != 'TDP' and col != 'Number of Threads' and col != 'Maximum Operating Temperature' and col != 'L2 Cache Size']
for column in keys:
    df[column + ' ln'] = np.log(df[column])         # Create new column in dataframe and transform data into ln(data)

X  = df[['Release Year']].values
y_liniar  = df[['L1 Cache Size ln', 'L2 Cache Size ln', 'Process Size (nm) ln', 'TDP ln', 'Base Clock ln', 'Boost Clock ln']].values
y_poly = df[['Number of Cores ln', 'Number of Threads ln', 'System Memory Frequency ln', 'Launch Price ($) ln']].values

# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 2)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Liniar regression for the rest of the columns
liniar_regressor = LinearRegression()
liniar_regressor.fit(X, y_liniar)

# Save liniar regression model and polynomial regression model
dump(liniar_regressor, './ML/CPU_liniar_regressor.joblib')
dump(poly_regressor, './ML/CPU_poly_regressor.joblib')