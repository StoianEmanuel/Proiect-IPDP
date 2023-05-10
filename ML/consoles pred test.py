from joblib import load
import pandas as pd
from utils import predicition, get_scores, add_boost, get_df, fill_with_mean

# Load linear regression model and polynomial regression model
linear_regressor = load('./ML/consoles_linear_regressor.joblib')
poly_regressor = load('./ML/consoles_poly_regressor.joblib')

year = [1980, 1990, 1996, 2000, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030] # set used for predictions

columns = ['Release Year', 'GPU Equivalent', 'Base Clock', 'RAM Size', 'RAM Frequency', 'Number of Exclusives',
            'Units Sold (millions)', 'CPU Equivalent', 'Launch Price']

lin_int_col  = [0]           # Specify columns that will be transformed into int
poly_int_col = [0, -1]

console_df = predicition(release_year = year, linear_regressor = linear_regressor, poly_regressor = poly_regressor,
                  degree = 7, columns = columns, lin_int_col = None, poly_int_col = poly_int_col)


# Get data from CPU table
db_path = './Data/gaming.sqlite'
cpu_query = '''SELECT Model, Manufacturer, [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
 [Number of Threads], [System Memory Frequency], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size], 
 TDP, [Maximum Operating Temperature] FROM CPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 
                        'System Memory Frequency', 'TDP']
cpu_df = get_df(db_path = db_path, db_query = cpu_query, keys = transform_columns)

cpu_df['Boost Clock'] = add_boost(cpu_df, 'Boost Clock')
cpu_df['TDP'] = fill_with_mean(cpu_df, 'TDP')
cpu_df['Maximum Operating Temperature'] = fill_with_mean(cpu_df, 'Maximum Operating Temperature')
cpu_df['Launch Price'] = fill_with_mean(cpu_df, 'Launch Price')


# Get data from GPU table
gpu_query = '''SELECT Model, Manufacturer, [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
 [Shading Units], [Transistors (millions)], [Memory Size], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size],
 TDP, [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed] FROM GPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Launch Price', 'TDP', 'Memory Bandwidth', 'Memory Clock Speed']
gpu_df = get_df(db_path = db_path, db_query = gpu_query, keys = transform_columns)

gpu_df['Boost Clock'] = add_boost(gpu_df, 'Boost Clock')
gpu_df['TDP'] = fill_with_mean(gpu_df, 'TDP')
gpu_df['Launch Price'] = fill_with_mean(gpu_df, 'Launch Price')

cols_n_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 
        'System Memory Frequency', 'Launch Price']
cols_rev_cpu = ['Process Size', 'TDP', 'Maximum Operating Temperature']
cpu_df['CPU Score'] = get_scores(cpu_df, scalable_columns = cols_n_cpu, scalable_columns_rev = cols_rev_cpu)


cols_n_gpu = ['Transistors (millions)', 'Shading Units', 'Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth', 'Memory Clock Speed', 'Launch Price']
cols_rev_gpu = ['Process Size', 'TDP']
gpu_df['GPU Score'] = get_scores(gpu_df, scalable_columns = cols_n_gpu, scalable_columns_rev = cols_rev_gpu)


#print('\n\n', cpu_df.sort_values('CPU Score')[['Model', 'CPU Score']].to_string(float_format='%.2f'), '\n\n')
#print(gpu_df.sort_values('GPU Score')[['Model', 'GPU Score']].to_string(float_format='%.2f'), '\n\n')

for index in range(len(console_df['GPU Equivalent'])):
    cpu_sub_score = 1000
    cpu_score = console_df.loc[index, 'CPU Equivalent']
    if cpu_score < 1.2:
        console_df.loc[index, 'CPU Equivalent'] = None
    else:
        for i in cpu_df.index:
            if abs(cpu_df.loc[i, 'CPU Score'] - cpu_score) < cpu_sub_score:
                cpu_sub_score = abs(cpu_df.loc[i, 'CPU Score'] - cpu_score)
                index_cpu = i
        console_df.loc[index, 'CPU Equivalent'] = cpu_df.loc[index_cpu, 'Manufacturer'] + ' ' + cpu_df.loc[index_cpu, 'Model']


    gpu_score = console_df.loc[index, 'GPU Equivalent']
    gpu_sub_score = 1000
    if gpu_score < 1.2:
        console_df.loc[index, 'GPU Equivalent'] = None
    else:
        for j in gpu_df.index:
            if abs(gpu_df.loc[j, 'GPU Score'] - gpu_score) < gpu_sub_score:
                gpu_sub_score = abs(gpu_df.loc[j, 'GPU Score'] - gpu_score)
                index_gpu = j
        console_df.loc[index, 'GPU Equivalent'] = gpu_df.loc[index_gpu, 'Manufacturer'] + ' ' + gpu_df.loc[index_gpu, 'Model']


print('''\nPredictii (dataframe):\nRelease Year | GPU Equivalent | Base Clock | RAM Size | RAM Frequency | Number of Exclusives
            Units Sold (millions) | CPU Equivalent | Launch Price\n''')

# Print sets of 3 columns from dataframe
for i in range(0, console_df.shape[1], 3):
    pd.options.display.max_rows = None
    print('\n', console_df.iloc[:, i:i+3])

# formatare pt JSON - LD