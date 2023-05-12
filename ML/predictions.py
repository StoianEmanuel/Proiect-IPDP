from joblib import load
import pandas as pd
from utils import predicition

class Processor:
    def __init__(self, linear_regressor_file, poly_regressor_file, year, columns, lin_int_col, poly_int_col, degree, filler_columns):
        self.linear_regressor = load(linear_regressor_file)
        self.poly_regressor = load(poly_regressor_file)
        self.year = year
        self.columns = columns
        self.lin_int_col = lin_int_col
        self.poly_int_col = poly_int_col
        self.degree = degree
        self.df = None
        self.filler_columns = filler_columns

    def read_data(self):
        self.df = predicition(release_year=self.year, linear_regressor=self.linear_regressor, poly_regressor=self.poly_regressor,
                         degree=self.degree, columns=self.columns, lin_int_col=self.lin_int_col, poly_int_col = self.poly_int_col,
                         filler_columns = self.filler_columns)
        
    def predict(self):
        if self.df is None:
            self.read_data()
        print(f"Predictii (dataframe):\n")
        for i in range(0, self.df.shape[1], 3):
            pd.options.display.max_rows = None
            print(self.df.iloc[:, i:i+3], '\n')
        

# Instanta a clasei Processor pentru CPU
cpu_processor = Processor(  linear_regressor_file = './ML/CPU_linear_regressor.joblib',
                poly_regressor_file = './ML/CPU_poly_regressor.joblib',
                year = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030],
                columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                    'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'],
                lin_int_col = [0, 1],
                poly_int_col = [0, 1, 2, 3],
                degree = 2,
                filler_columns = ['Model'])
# Metoda predict pentru CPU
cpu_processor.predict()

# grafic real / estimated + metrica 
# spline vs poly vs lin
# body -- vector pt release year
# json -- data returned

# Instanta a clasei Processor pentru GPU
cpu_processor = Processor(  linear_regressor_file = './ML/GPU_linear_regressor.joblib',
                poly_regressor_file = './ML/GPU_poly_regressor.joblib',
                year = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030],
                columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP (W)', 'Core Base Clock (GHz)', 'Core Boost Clock (GHz)',
                           'Memory Bandwidth (GB/s)', 'Shading Units', 'Memory Size (GB)', 'Memory Clock Speed (MHz)', 'Launch Price ($)'],
                lin_int_col  = [0, 1, 2],
                poly_int_col = [0, 2, -1],
                degree = 2,
                filler_columns = ['Model', 'Manufacturer', 'DirectX'])
# Metoda predict pentru GPU
cpu_processor.predict()