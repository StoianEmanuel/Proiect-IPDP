from joblib import load
import pandas as pd
from utils import predicition

# Load linear regression model and polynomial regression model
linear_regressor = load('./ML/GPU_linear_regressor.joblib')
poly_regressor = load('./ML/GPU_poly_regressor.joblib')
year = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030] # set used for predictions
columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP (W)', 'Core Base Clock (GHz)', 'Core Boost Clock (GHz)', 'Memory Bandwidth (GB/s)', 'Shading Units', 'Memory Size (GB)', 'Memory Clock Speed (MHz)', 'Launch Price ($)']
lin_int_col  = [0, 1, 2]
poly_int_col = [0, 2, -1]

df = predicition(release_year = year, linear_regressor = linear_regressor, poly_regressor = poly_regressor, degree = 2, columns = columns, lin_int_col = lin_int_col, poly_int_col = poly_int_col)
print("Predictii (dataframe):\n' Release Year | Transistors (millions) | Process Size (nm) | TDP (W) | Core Base Clock (GHz) | Core Boost Clock (GHz) | Memory Bandwidth (GB/s) | 'Shading Units | Memory Size (GB) | Memory Clock Speed (MHz) | Launch Price ($)\n")

# Parcurgem coloanele în grupuri de câte 3 și afișăm fiecare grup
for i in range(0, df.shape[1], 3):
    pd.options.display.max_rows = None
    print(df.iloc[:, i:i+3])
# Exportăm DataFrame-ul în fișierul CSV cu separatori tab și virgulă
#df.to_csv('rezultat.csv', sep=',', index=False)