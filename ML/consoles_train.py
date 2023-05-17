import numpy as np
import math
from utils import add_boost, get_df, jaccard_similarity, get_scores, fill_column_with_mean_value
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from joblib import dump


# Get data from Consoles table
db_path = './Data/gaming.sqlite'
console_query = '''SELECT Name AS [Consoles Name], [Release Year], [Units Sold (millions)], [Number of Exclusives],
 [CPU Equivalent] AS [CPU Name], [CPU Frequency] AS [Base Clock], [GPU Equivalent] AS [GPU Name], [RAM Size], [RAM Frequency], 
 [Launch Price ($)] AS [Launch Price] FROM Consoles'''

transform_columns = ['Base Clock', 'RAM Size', 'RAM Frequency', 'Launch Price']
console_df = get_df(db_path = db_path, db_query = console_query, keys = transform_columns)


# Get data from CPU table
cpu_query = '''SELECT Model, Manufacturer, [Release Year], [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
 [Number of Threads], [System Memory Frequency], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size] FROM CPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'System Memory Frequency']
cpu_df = get_df(db_path = db_path, db_query = cpu_query, keys = transform_columns)

cpu_df['Boost Clock'] = add_boost(cpu_df, 'Boost Clock')
cpu_df['Boost Clock'] *= 7.5
cpu_df['Base Clock'] *= 5
cpu_df['Process Size'] *= 0.1
cpu_df['L2 Cache Size'] *= 5
cpu_df['L1 Cache Size'] *= 4
cpu_df['Number of Threads'] *= 2
cpu_df['Number of Cores'] *= 2.5
cpu_df['System Memory Frequency'] *= 10000


# Get data from GPU table
gpu_query = '''SELECT Model, Manufacturer, [Release Year], [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
 [Shading Units], [Transistors (millions)], [Memory Size], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size],
 [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed], [Integration Density] FROM GPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Launch Price', 'Memory Bandwidth', 'Memory Clock Speed',
                      'Integration Density']
gpu_df = get_df(db_path = db_path, db_query = gpu_query, keys = transform_columns)

gpu_df['Boost Clock'] = add_boost(gpu_df, 'Boost Clock')
gpu_df['Boost Clock'] *= 1.1
gpu_df['Transistors (millions)'] *= 1000000

# Fill 0 values in gpu_df dataframe with mean value of neighboring rows
gpu_df['Process Size'] = fill_column_with_mean_value(df = gpu_df, column = 'Process Size', interval_columns = ['Release Year'],
    cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']],
               ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])['Process Size']

gpu_df['Integration Density'] = fill_column_with_mean_value(df = gpu_df, column = 'Integration Density', interval_columns = ['Release Year'],
    cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']],
               ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])['Integration Density']

# store "CPU Score" values in column "CPU Score" from cpu_df dataframe
cols_n_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 
                'System Memory Frequency']
cols_rev_cpu = ['Process Size']
cpu_df['CPU Score'] = get_scores(cpu_df, scalable_columns = cols_n_cpu, scalable_columns_rev = None)

# store "GPU Score" values in column "GPU Score" from gpu_df dataframe
cols_n_gpu = ['Transistors (millions)', 'Shading Units', 'Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth',
               'Memory Clock Speed', 'Integration Density']
cols_rev_gpu = ['Process Size']
gpu_df['GPU Score'] = get_scores(gpu_df, scalable_columns = cols_n_gpu, scalable_columns_rev = cols_rev_gpu)


# Find "GPU Score" and "CPU Score" values for every "CPU Equivalent"/ "GPU Equivalent" stored in console_df dataframe 
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

# Change values to log(values) for easier predictions
for column in console_df.columns:
    if 'Name' not in column and column != 'Release Year' and column != 'Base Clock' and 'RAM' not in column:
        console_df[column] = np.log(console_df[column] + math.e)

console_df['Base Clock'] = np.log(console_df['Base Clock'])

# Change -inf to min(console_df['RAM Size'])
min_value = math.log(console_df['RAM Size'].mean())
console_df['RAM Size'] = np.log(console_df['RAM Size'])

for i in range(len(console_df['RAM Size'])):
    if min_value > console_df.loc[i, 'RAM Size'] and console_df.loc[i, 'RAM Size'] != -np.inf:
        min_value = console_df.loc[i, 'RAM Size']

for i in range(len(console_df['RAM Size'])):
    if console_df.loc[i, 'RAM Size'] == -np.inf:
        console_df.loc[i, 'RAM Size'] = min_value

'''for i in range(0, console_df.shape[1], 3):
    pd.options.display.max_rows = None
    print(console_df.iloc[:, i:i+3])'''


X  = console_df[['Release Year']].values
y_linear = console_df[['Base Clock', 'RAM Size', 'RAM Frequency']].values
y_poly1  = console_df[['CPU Score', 'GPU Score']].values
y_poly2  = console_df[['Number of Exclusives', 'Units Sold (millions)', 'Launch Price']].values


poly_features = PolynomialFeatures(degree = 2)
X_poly = poly_features.fit_transform(X)
poly_regressor1 = LinearRegression()
poly_regressor1.fit(X_poly, y_poly1)


poly_features = PolynomialFeatures(degree = 7)
X_poly = poly_features.fit_transform(X)
poly_regressor2 = LinearRegression()
poly_regressor2.fit(X_poly, y_poly2)

linear_regressor = LinearRegression()
linear_regressor.fit(X, y_linear)

dump(linear_regressor, './ML/consoles_linear_regressor.joblib')
dump(poly_regressor1, './ML/consoles_poly_regressor1.joblib')
dump(poly_regressor2, './ML/consoles_poly_regressor2.joblib')