import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump
from utils import get_df_for_gpu, remove_columns


db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM GPU WHERE [Release Year] > 1985 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0'

# Define set of columns from db of string or integer values
Transform_col   = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP']
Int_col         = ['Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Launch Price ($)']
df = get_df_for_gpu(db_path, db_query, Transform_col, None, None)

# Remove unused columns
keys = Transform_col + Int_col
df = remove_columns(df, keys)

df['Shading Units ln'] = df['Shading Units'].replace(0, 1)
df['Shading Units ln'] = np.log(df['Shading Units ln'])

keys = [col for col in keys if col != 'Release Year' and col != 'Shading Units']
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