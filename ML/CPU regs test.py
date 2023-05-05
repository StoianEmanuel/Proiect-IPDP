from joblib import load
import pandas as pd
from utils import predicition

# Load linear regression model and polynomial regression model
linear_regressor = load('./ML/CPU_linear_regressor.joblib')
poly_regressor = load('./ML/CPU_poly_regressor.joblib')
year = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030] # set used for predictions
columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)']
lin_int_col  = [0, 1]
poly_int_col = [0, 1, 2, 3]

df = predicition(release_year = year, linear_regressor = linear_regressor, poly_regressor = poly_regressor, degree = 2, columns = columns, lin_int_col = lin_int_col, poly_int_col = poly_int_col)
print("Predictii (dataframe):\n' Release Year | Process Size (nm) | TDP (W) | Base Clock (GHz) | Boost Clock (GHz) | L1 Cache Size (GB) | L2 Cache Size (GB) | Number of Cores | Number of Threads | System Memory Frequency (MHz) | Launch Price ($)\n")

# Parcurgem coloanele în grupuri de câte 7 și afișăm fiecare grup
for i in range(0, df.shape[1], 3):
    pd.options.display.max_rows = None
    print(df.iloc[:, i:i+3])
# Exportăm DataFrame-ul în fișierul CSV cu separatori tab și virgulă
#df.to_csv('rezultat.csv', sep=',', index=False)