import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump
from utils import get_df_for_cpu, remove_columns


db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0'

# Define set of columns from db of string or integer values
Transform_col   = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 'System Memory Frequency', 'TDP']
Int_col         = ['Release Year', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']

df = get_df_for_cpu(db_path, db_query, Transform_col)

# Remove unused columns
keys = Transform_col + Int_col
df = remove_columns(df, keys)

df['Number of Threads ln'] = df['Number of Threads'].replace(0, 0.5)
df['Number of Threads ln'] = np.log(df['Number of Threads ln'])

df['L2 Cache Size ln'] = df['L2 Cache Size'].replace(0, 0.00000001)
df['L2 Cache Size ln'] = np.log(df['L2 Cache Size ln'])

keys = [col for col in keys if col != 'Release Year' and col != 'Number of Threads' and col != 'L2 Cache Size']
for column in keys:
    df[column + ' ln'] = np.log(df[column])         # Create new column in dataframe and transform data into ln(data)

X  = df[['Release Year']].values
y_linear  = df[['Process Size (nm) ln', 'TDP ln', 'Base Clock ln', 'Boost Clock ln', 'L1 Cache Size ln', 'L2 Cache Size ln']].values
y_poly = df[['Number of Cores ln', 'Number of Threads ln', 'System Memory Frequency ln', 'Launch Price ($) ln']].values

# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 2)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Linear regression for the rest of the columns
linear_regressor = LinearRegression()
linear_regressor.fit(X, y_linear)

# Save linear regression model and polynomial regression model
dump(linear_regressor, './ML/CPU_linear_regressor.joblib')
dump(poly_regressor, './ML/CPU_poly_regressor.joblib')