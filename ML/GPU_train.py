import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump
from utils import get_df, remove_columns, add_boost


db_path = './Data/gaming.sqlite'
db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1989 AND [Transistors (millions)] > 0 AND [Integration Density] IS NOT NULL AND
            [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL 
            AND [Memory Clock Speed (Effective)] IS NOT NULL AND [TDP] IS NOT NULL AND [Launch Price ($)] > 0'''

# Define set of columns from db of string or integer values
string_col   = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP',
                    'Integration Density']
real_col         = ['Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Launch Price ($)']

df = get_df(db_path, db_query, string_col, None, None)
df['Core Boost Clock'] = add_boost(df, 'Core Boost Clock')
#print(df[['Release Year', 'Integration Density']].values)

# Remove unused columns
keys = string_col + real_col
df = remove_columns(df, keys)

df['Shading Units'] = df['Shading Units'].replace(0, 1)

keys = [col for col in keys if col != 'Release Year']
for column in keys:
    df[column] = np.log(df[column])         # Create new column in dataframe and transform data into ln(data)

X  = df[['Release Year']].values
y_linear  = df[['Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock', 
                'Memory Bandwidth', 'Memory Size']].values
y_poly = df[['Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)']].values

# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 2)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Linear regression for the rest of the columns
linear_regressor = LinearRegression()
linear_regressor.fit(X, y_linear)

# Save linear regression model and polynomial regression model
dump(linear_regressor, './ML/GPU_linear_regressor.joblib')
dump(poly_regressor, './ML/GPU_poly_regressor.joblib')