import pandas as pd
import numpy as np
import math
from utils import add_boost, fill_with_mean_column, get_df, jaccard_similarity, get_scores, fill_column_with_mean_value
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer
from joblib import dump

from sklearn.pipeline import make_pipeline


# Get data from Consoles table
db_path = './Data/gaming.sqlite'
console_query = '''SELECT Name AS [Consoles Name], [Release Year], [Units Sold (millions)], [Number of Exclusives],
 [CPU Equivalent] AS [CPU Name], [CPU Frequency] AS [Base Clock], [GPU Equivalent] AS [GPU Name], [RAM Size], [RAM Frequency], 
 [Launch Price ($)] AS [Launch Price] FROM Consoles'''

transform_columns = ['Base Clock', 'RAM Size', 'RAM Frequency', 'Launch Price']
console_df = get_df(db_path = db_path, db_query = console_query, keys = transform_columns)


# Get data from CPU table
cpu_query = '''SELECT Model, Manufacturer, [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
 [Number of Threads], [System Memory Frequency], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size], 
 TDP, [Maximum Operating Temperature] FROM CPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 
                        'System Memory Frequency', 'TDP']
cpu_df = get_df(db_path = db_path, db_query = cpu_query, keys = transform_columns)

cpu_df['Boost Clock'] = add_boost(cpu_df, 'Boost Clock')
cpu_df['TDP'] = fill_with_mean_column(cpu_df, 'TDP')
cpu_df['Maximum Operating Temperature'] = fill_with_mean_column(cpu_df, 'Maximum Operating Temperature')


# Get data from GPU table
gpu_query = '''SELECT Model, Manufacturer, [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
 [Shading Units], [Transistors (millions)], [Memory Size], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size],
 TDP, [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed], [Integration Density] FROM GPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Launch Price', 'TDP', 'Memory Bandwidth', 'Memory Clock Speed', 'Integration Density']
gpu_df = get_df(db_path = db_path, db_query = gpu_query, keys = transform_columns)

gpu_df['Boost Clock'] = add_boost(gpu_df, 'Boost Clock')
gpu_df['TDP'] = fill_with_mean_column(gpu_df, 'TDP')
gpu_df['Integration Density'] = fill_with_mean_column(gpu_df, 'Integration Density')

cols_n_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 
        'System Memory Frequency', 'Launch Price']
cols_rev_cpu = ['Process Size', 'TDP', 'Maximum Operating Temperature']
cpu_df['CPU Score'] = get_scores(cpu_df, scalable_columns = cols_n_cpu, scalable_columns_rev = cols_rev_cpu)


cols_n_gpu = ['Transistors (millions)', 'Shading Units', 'Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth',
               'Memory Clock Speed', 'Launch Price', 'Integration Density']
cols_rev_gpu = ['Process Size', 'TDP']
gpu_df['GPU Score'] = get_scores(gpu_df, scalable_columns = cols_n_gpu, scalable_columns_rev = cols_rev_gpu)


for i in range(len(console_df['Consoles Name'])):
    cpu_equivalent = console_df.loc[i, 'CPU Name']
    gpu_equivalent = console_df.loc[i, 'GPU Name']
    console_df.loc[i, 'CPU Score'] = 0
    console_df.loc[i, 'GPU Score'] = 0

    if cpu_equivalent:
        for j in range(len(cpu_df['Model'])):
            cpu_name = cpu_df.loc[j, 'Manufacturer'] + ' ' + cpu_df.loc[j, 'Model']
            jacard_similarity_score = jaccard_similarity(cpu_equivalent, cpu_name)
            if jacard_similarity_score > 95:
                console_df.loc[i, 'CPU Score'] = cpu_df.loc[j, 'CPU Score']
                break

    if gpu_equivalent:
        for k in range(len(gpu_df['Model'])):
            gpu_name = gpu_df.loc[k, 'Manufacturer'] + ' ' + gpu_df.loc[k, 'Model']
            jacard_similarity_score = jaccard_similarity(gpu_equivalent, gpu_name)
            if jacard_similarity_score > 95:
                console_df.loc[i, 'GPU Score'] = gpu_df.loc[k, 'GPU Score']
                break


for i in range(0, console_df.shape[1], 3):
    pd.options.display.max_rows = None
    print(console_df.iloc[:, i:i+3])

for column in console_df.columns:
    if 'Name' not in column and column != 'Release Year' and column != 'Base Clock' and 'RAM' not in column:
        console_df[column] = np.log(console_df[column] + math.e)

console_df['Base Clock'] = np.log(console_df['Base Clock'])


# get min value
min_value = math.log(console_df['RAM Size'].mean())
console_df['RAM Size'] = np.log(console_df['RAM Size'])

for i in range(len(console_df['RAM Size'])):
    if min_value > console_df.loc[i, 'RAM Size'] and console_df.loc[i, 'RAM Size'] != -np.inf:
        min_value = console_df.loc[i, 'RAM Size']

for i in range(len(console_df['RAM Size'])):
    if console_df.loc[i, 'RAM Size'] == -np.inf:
        console_df.loc[i, 'RAM Size'] = min_value

min_value = math.log(console_df['RAM Frequency'].mean())
console_df['RAM Frequency'] = np.log(console_df['RAM Frequency'])

for i in range(len(console_df['RAM Frequency'])):
    if min_value > console_df.loc[i, 'RAM Frequency'] and console_df.loc[i, 'RAM Frequency'] != -np.inf:
        min_value = console_df.loc[i, 'RAM Frequency']

for i in range(len(console_df['RAM Frequency'])):
    if console_df.loc[i, 'RAM Frequency'] == -np.inf:
        console_df.loc[i, 'RAM Frequency'] = min_value

for i in range(0, console_df.shape[1], 3):
    pd.options.display.max_rows = None
    print(console_df.iloc[:, i:i+3])


X  = console_df[['Release Year']].values
y_linear  = console_df[['GPU Score', 'Base Clock', 'RAM Size', 'RAM Frequency']].values
y_poly = console_df[['Number of Exclusives', 'Units Sold (millions)', 'CPU Score', 'Launch Price']].values

# Polynomial regression for 'Shading Units', 'Memory Size', 'Memory Clock Speed', Launch Price ($)
poly_features = PolynomialFeatures(degree = 7)
X_poly = poly_features.fit_transform(X)
poly_regressor = LinearRegression()
poly_regressor.fit(X_poly, y_poly)

# Linear regression for the rest of the columns
linear_regressor = LinearRegression()
linear_regressor.fit(X, y_linear)

# Save linear regression model and polynomial regression model
dump(linear_regressor, './ML/consoles_linear_regressor.joblib')
dump(poly_regressor, './ML/consoles_poly_regressor.joblib')