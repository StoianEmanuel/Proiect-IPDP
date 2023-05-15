from joblib import load
from matplotlib import pyplot as plt
import pandas as pd
from utils import predicition, get_df, add_boost, remove_columns
from sklearn.metrics import mean_squared_error

class Processor:
    def __init__(self, linear_regressor_file, poly_regressor_file, year, columns, lin_int_col, poly_int_col, degree,
                 db_path, db_query, string_columns):
        self.linear_regressor = load(linear_regressor_file)
        self.poly_regressor = load(poly_regressor_file)
        self.year = year
        self.columns = columns
        self.lin_int_col = lin_int_col
        self.poly_int_col = poly_int_col
        self.degree = degree
        self.predicted_df = None
        self.original_df = get_df(db_path, db_query, string_columns, None, None)
        self.original_df = remove_columns(self.original_df, columns)


    def read_data(self):
        self.predicted_df = predicition(release_year=self.year, linear_regressor=self.linear_regressor, poly_regressor=self.poly_regressor,
                         degree=self.degree, columns=self.columns, lin_int_col=self.lin_int_col, poly_int_col = self.poly_int_col)


    def get_df(self):
        return self.predicted_df

    
    def add_boost_clock(self, column):
        self.original_df[column] = add_boost(self.original_df, column)


    def export_mse_to_csv(self, remove_from_df_rows = [], output_path = './predition.txt', merge_column = 'Release Year'):
        # Remove specified rows from original_df
        #print(self.original_df.shape, self.predicted_df.shape)
        original_df_aux = self.original_df
        predicted_df_aux = self.predicted_df

        if len(remove_from_df_rows):
            for column, remove_list_values in remove_from_df_rows:
                original_df_aux = original_df_aux[~original_df_aux[column].isin(remove_list_values)]
                predicted_df_aux = predicted_df_aux[~predicted_df_aux[column].isin(remove_list_values)]
        
        # remove data that can't be used and sort rows by merge_column values
        original_df_aux = original_df_aux[original_df_aux[merge_column].isin(predicted_df_aux[merge_column].values)]
        original_df_aux = original_df_aux.sort_values(merge_column).reset_index(drop = True)
        predicted_df_aux = predicted_df_aux.sort_values(merge_column).reset_index(drop = True)
        # Calculate Mean Squared Error (MSE) for each column
        mse_dict = {}
        mse_total = 0
        l = 0
        n = len(predicted_df_aux[merge_column].values)
        m = len(original_df_aux[merge_column].values)

        for column in self.columns:

            if column != merge_column:
                mse_i = 0
                nr = 0
                for i in range(0, n):
                    for j in range(l, m):
                        if predicted_df_aux.loc[i, merge_column] == original_df_aux.loc[j, merge_column]:
                            l += 1
                            nr += 1
                            mse_i += (predicted_df_aux.loc[i, column] - original_df_aux.loc[j, column])**2
                        else:
                            break
                if nr != 0:
                    mse_i /= nr
                l = 0
                #mse = mean_squared_error(original_df_aux[column], predicted_df_aux[column])
                mse_dict[column] = mse_i
                mse_total += mse_i
        
        with open(output_path, 'w') as f:
            f.write('Column,MSE\n')
            for column, mse in mse_dict.items():
                f.write(f'{column}={mse}\n')

            f.write(f'\nTotal MSE={mse_total}\n')
            f.write(f'Polynomial Regression Degree={self.degree}')
    

    def get_graphs(self, columns, merge_column = 'Release Year'):
        # Generate plots for each column
        for column in columns:
            plt.figure()
            plt.plot(self.original_df[merge_column], self.original_df[column], 'bo', label='Actual')
            plt.plot(self.predicted_df[merge_column], self.predicted_df[column], 'r', label='Predicted')
            plt.legend(loc='best')
            plt.title(column)
            plt.xlabel(merge_column)
            plt.ylabel(column)
            plt.show()


def prediction_cpu(years = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030]):
    cpu_processor = Processor (linear_regressor_file = './ML/CPU_linear_regressor.joblib',
                    poly_regressor_file = './ML/CPU_poly_regressor.joblib',
                    year = years,
                    columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                        'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'],
                    lin_int_col = [0, 1],
                    poly_int_col = [0, 1, 2, 3],
                    degree = 10,
                    db_path = './Data/gaming.sqlite',
                    db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] 
IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0 AND [Maximum Operating Temperature]
IS NOT NULL AND [TDP] IS NOT NULL''',
                    string_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
                    'System Memory Frequency', 'TDP'])
    
    cpu_processor.read_data()
    cpu_processor.add_boost_clock('Boost Clock')

    cpu_processor.get_graphs(['Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                       'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'])
    
    cpu_processor.export_mse_to_csv(output_path = './ML/predition_cpu.txt', merge_column = 'Release Year')
    # grafic real / estimated + metrica 
    # spline vs poly vs lin
    # json -- data returned


def prediction_gpu(years = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030]):
    gpu_processor = Processor (linear_regressor_file = './ML/GPU_linear_regressor.joblib',
                    poly_regressor_file = './ML/GPU_poly_regressor.joblib',
                    year = years,
                    columns = ['Release Year', 'Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)'],
                    lin_int_col  = [0, 2],
                    poly_int_col = [1, 2, 3],
                    degree = 2,
                    db_path = './Data/gaming.sqlite',
                    db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1989 AND [Transistors (millions)] > 0 AND [Integration Density] 
                    IS NOT NULL AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND 
                    [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [TDP] IS NOT NULL AND [Launch Price ($)] > 0''',
                    string_columns = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP',
                    'Integration Density'])
    gpu_processor.read_data()
    gpu_processor.add_boost_clock('Core Boost Clock')
    
    gpu_processor.get_graphs(['Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)'])
    
    gpu_processor.export_mse_to_csv(output_path = './ML/predition_gpu.txt', merge_column = 'Release Year')

#prediction_cpu()

prediction_gpu()