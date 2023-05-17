from flask import Flask, request, jsonify
import sqlite3, json, os
#import numpy as np
#from joblib import load
import sys

import pandas as pd
sys.path.insert(0, './ML')
from utils import remove_columns, reorder_columns, add_size_units_to_df_values
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

cpu_processor = Processor(linear_regressor_file = './ML/CPU_linear_regressor.joblib',
                poly_regressor_file = './ML/CPU_poly_regressor.joblib',
                year = years_int,
                columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                    'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'],
                lin_int_col  = [0, 1],
                poly_int_col = [0, 1, 2, 3],
                degree = 10)
        # Metoda predict pentru GPU
cpu_processor.read_data()
df = cpu_processor.get_df()
columns = cpu_processor.columns

columns_to_update = ['TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
            'Maximum Operating Temperature', 'System Memory Frequency']
df = reorder_columns(df, [0, 1, 8, 9, 3, 4, 5, 6, 10, 2, 7, 11])
for i in range(0, df.shape[1], 3):
    pd.options.display.max_rows = None
    print(df.iloc[:, i:i+3], '\n')
df = add_size_units_to_df_values(df, columns_to_update)
print(df)
for column in columns:
    if column not in columns_to_update:
        df[column] = df[column].astype(int)
info = df.to_dict(orient='records')
print(info)