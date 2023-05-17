import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump
from utils import get_df, remove_columns, add_boost


db_path = './Data/gaming.sqlite'
db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] 
IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0 AND [Maximum Operating Temperature]
IS NOT NULL AND [TDP] IS NOT NULL'''

# Define set of columns from db of string or integer values
string_col  = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
                    'System Memory Frequency', 'TDP']
real_col    = ['Release Year', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']

df = get_df(db_path, db_query, string_col)
df['Boost Clock'] = add_boost(df, 'Boost Clock')

# Remove unused columns
keys = string_col + real_col
df = remove_columns(df, keys)

df['Number of Threads'] = df['Number of Threads'].replace(0, 0.5)
df['L2 Cache Size'] = df['L2 Cache Size'].replace(0, 0.00000001)

keys = [column for column in keys if column != 'Release Year']
for column in keys:
    df[column] = np.log(df[column])


X  = df[['Release Year']].values
y_linear  = df[['Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature']].values
y_poly = df[['Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)']].values


# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 10)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Linear regression for the rest of the columns
linear_regressor = LinearRegression()
linear_regressor.fit(X, y_linear)

# Save linear regression model and polynomial regression model
dump(linear_regressor, './ML/CPU_linear_regressor.joblib')
dump(poly_regressor, './ML/CPU_poly_regressor.joblib')