from flask import Flask, request, jsonify
import sqlite3, json, os
#import numpy as np
#from joblib import load
import sys
sys.path.insert(0, './ML')
from utils import remove_columns, reorder_columns, add_size_units_to_df_values, fill_column_with_mean_value
from consoles_test import consoles_prediction
from predictions import Processor
numbers= [1990,1995,2000, 2010, 2020]
years_int = []
for number in numbers:
    n = int(number)
    if 1990 <= n <= 2030:
        years_int.append(n)

years_int = sorted(set(years_int))
years_int = list(years_int)

gpu_processor = Processor (year = years_int,
                    linear_regressor_file = './ML/GPU_linear_regressor.joblib',
                    lin_int_col  = [0, 2],

                    poly_regressor_file1 = './ML/GPU_poly_regressor.joblib',
                    poly_int_col1 = [1, 2, 3],
                    degree1 = 2,
                    
                    columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)'],
                    
                    db_path = './Data/gaming.sqlite',
                    db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1989 AND [Transistors (millions)] > 0 AND [Integration Density] 
                    IS NOT NULL AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND 
                    [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [TDP] IS NOT NULL AND [Launch Price ($)] > 0''',

                    string_columns = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 
                                      'Memory Size', 'TDP', 'Integration Density'])
# Metoda predict pentru GPU
gpu_processor.read_data()
df = gpu_processor.get_df()

columns = gpu_processor.columns

df = reorder_columns(df, [0, 1, 2, 8, 7, 4, 5, 9, 6, 10, 3, 11])
columns_to_update = ['TDP', 'Core Base Clock', 'Core Boost Clock',
    'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Memory Clock Speed (Effective)']
df = add_size_units_to_df_values(df, columns_to_update)
print(df)
for column in columns:
    if column not in columns_to_update:
        df[column] = df[column].astype(int)
info = df.to_dict(orient='records')
#print(info)

"""gpu_processor = Processor (year = years_int,
                    linear_regressor_file = './ML/GPU_linear_regressor.joblib',
                    lin_int_col  = [0, 2],

                    poly_regressor_file1 = './ML/GPU_poly_regressor.joblib',
                    poly_int_col1 = [1, 2, 3],
                    degree1 = 2,
                    
                    columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)'],
                    
                    db_path = './Data/gaming.sqlite',
                    db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1989 AND [Transistors (millions)] > 0 AND [Integration Density] 
                    IS NOT NULL AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND 
                    [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [TDP] IS NOT NULL AND [Launch Price ($)] > 0''',

                    string_columns = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 
                                      'Memory Size', 'TDP', 'Integration Density'])"""

gpu = gpu_processor.original_df
#print(gpu.columns)
gpu = fill_column_with_mean_value(gpu, 'TDP', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple', 'ARM']]])
gpu = fill_column_with_mean_value(gpu, 'Memory Bandwidth', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']], ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])
gpu = fill_column_with_mean_value(gpu, 'Memory Size', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']], ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])
gpu = fill_column_with_mean_value(gpu, 'Launch Price ($)', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']], ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])
gpu = fill_column_with_mean_value(gpu, 'Transistors (millions)', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']], ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])
gpu = fill_column_with_mean_value(gpu, 'Integration Density', interval_columns = ['Release Year'], cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']], ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])



gpu_processor.original_df = gpu
gpu_processor.print_data(data_type = 'original')

print(gpu)