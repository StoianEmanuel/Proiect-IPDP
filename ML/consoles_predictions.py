from joblib import load
from matplotlib import pyplot as plt
import pandas as pd
from utils import add_boost, add_size_units_to_df_values, fill_column_with_mean_value, get_df, get_scores, jaccard_similarity, predicition, integer_or_float_value


class ConsolePredictor:
    def __init__(self, database_path = './Data/gaming.sqlite', linear_regressor_path=None,
                 polynomial_regressor_path1=None, poly_degree1=None,
                 polynomial_regressor_path2=None, poly_degree2=None):
        self.database_path = database_path
        self.linear_regressor_path = linear_regressor_path

        self.polynomial_regressor_path1 = polynomial_regressor_path1
        self.poly_degree1 = poly_degree1

        self.polynomial_regressor_path2 = polynomial_regressor_path2
        self.poly_degree2 = poly_degree2
        
        console_query = '''SELECT Name AS [Consoles Name], [Release Year], [Units Sold (millions)], [Number of Exclusives],
        [CPU Equivalent] AS [CPU Name], [CPU Frequency], [GPU Equivalent] AS [GPU Name], [RAM Size], [RAM Frequency], 
        [Launch Price ($)] AS [Launch Price] FROM Consoles'''
        transform_columns = ['CPU Frequency', 'RAM Size', 'RAM Frequency', 'Launch Price']
        self.original_df  = get_df(db_path = database_path, db_query = console_query, keys = transform_columns)
        
        self.predicted_df = pd.DataFrame()
        self.cpu_df = pd.DataFrame()
        self.gpu_df = pd.DataFrame()
        
    
    def set_data_for_df(self):
        db_path = self.database_path
        cpu_query = '''SELECT Model, Manufacturer, [Release Year], [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
    [Number of Threads], [System Memory Frequency], [Process Size (nm)] AS [Process Size] FROM CPU'''
        transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'System Memory Frequency']
        self.cpu_df = get_df(db_path=db_path, db_query=cpu_query, keys=transform_columns)
        
        self.cpu_df['Boost Clock'] = add_boost(self.cpu_df, 'Boost Clock')
        self.cpu_df['Base Clock'] *= 5
        self.cpu_df['Boost Clock'] *= 7.5
        self.cpu_df['Process Size'] *= 0.1
        self.cpu_df['L2 Cache Size'] *= 5
        self.cpu_df['L1 Cache Size'] *= 4
        self.cpu_df['Number of Threads'] *= 2
        self.cpu_df['Number of Cores'] *= 2.5
        self.cpu_df['System Memory Frequency'] *= 10000

        gpu_query = '''SELECT Model, Manufacturer, [Release Year], [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
    [Shading Units], [Transistors (millions)], [Memory Size], [Process Size (nm)] AS [Process Size],
    [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed], [Integration Density] FROM GPU'''
        transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth', 'Memory Clock Speed',
                             'Integration Density']

        self.gpu_df = get_df(db_path=db_path, db_query=gpu_query, keys=transform_columns)
        self.gpu_df['Transistors (millions)'] *= 1000000
        self.gpu_df['Boost Clock'] = add_boost(self.gpu_df, 'Boost Clock')
        self.gpu_df['Boost Clock'] *= 1.1

        self.gpu_df['Process Size'] = fill_column_with_mean_value(df=self.gpu_df, column='Process Size',
                                                             interval_columns=['Release Year'],
                                                             cases=[['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']],
                                                                    ['Manufacturer', ['AMD']],
                                                                    ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']],
                                                                    ['Manufacturer', ['ATI', '3dfx']]])['Process Size']

        self.gpu_df['Integration Density'] = fill_column_with_mean_value(df=self.gpu_df, column='Integration Density',
                                                                    interval_columns=['Release Year'],
                                                                    cases=[['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']],
                                                                           ['Manufacturer', ['AMD']],
                                                                           ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']],
                                                                           ['Manufacturer', ['ATI', '3dfx']]])['Integration Density']

        cols_n_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads',
                      'System Memory Frequency']
        self.cpu_df['CPU Score'] = get_scores(self.cpu_df, scalable_columns=cols_n_cpu, scalable_columns_rev=None)

        cols_n_gpu = ['Transistors (millions)', 'Shading Units', 'Base Clock', 'Boost Clock', 'Memory Size',
                      'Memory Bandwidth',
                      'Memory Clock Speed', 'Integration Density']
        cols_rev_gpu = ['Process Size']
        self.gpu_df['GPU Score'] = get_scores(self.gpu_df, scalable_columns=cols_n_gpu, scalable_columns_rev=cols_rev_gpu)

        for i in range(len(self.original_df['Consoles Name'])):
            cpu_equivalent = self.original_df.loc[i, 'CPU Name']
            gpu_equivalent = self.original_df.loc[i, 'GPU Name']
            self.original_df.loc[i, 'CPU Score'] = 0
            self.original_df.loc[i, 'GPU Score'] = 0

            if cpu_equivalent:
                for j in range(len(self.cpu_df['Model'])):
                    cpu_name = self.cpu_df.loc[j, 'Manufacturer'] + ' ' + self.cpu_df.loc[j, 'Model']
                    jacard_similarity_score = jaccard_similarity(cpu_equivalent, cpu_name)
                    if jacard_similarity_score > 95:
                        self.original_df.loc[i, 'CPU Score'] = self.cpu_df.loc[j, 'CPU Score']
                        break

            if gpu_equivalent:
                for k in range(len(self.gpu_df['Model'])):
                    gpu_name = self.gpu_df.loc[k, 'Manufacturer'] + ' ' + self.gpu_df.loc[k, 'Model']
                    jacard_similarity_score = jaccard_similarity(gpu_equivalent, gpu_name)
                    if jacard_similarity_score > 95:
                        self.original_df.loc[i, 'GPU Score'] = self.gpu_df.loc[k, 'GPU Score']
                        break

    def prediction_for_consoles(self, years=[]):
        linear_regressor = load(self.linear_regressor_path)
        poly_regressor1  = load(self.polynomial_regressor_path1)
        poly_regressor2  = load(self.polynomial_regressor_path2)

        columns = ['Release Year', 'CPU Frequency', 'RAM Size', 'RAM Frequency', 'CPU Equivalent', 'GPU Equivalent',
                   'Number of Exclusives', 'Units Sold (millions)', 'Launch Price']


        self.predicted_df = predicition(release_year=years, columns=columns, linear_regressor=linear_regressor,
                                 lin_int_col=None,
                                 poly_regressor1=poly_regressor1, poly_degree1=self.poly_degree1,
                                 poly_int_col1=None,
                                 poly_regressor2=poly_regressor2, poly_degree2=self.poly_degree2,
                                 poly_int_col2=None)

        self.predicted_df['RAM Size'] *= 0.55
        self.predicted_df['RAM Frequency'] *= 1000
        self.predicted_df['RAM Frequency'] = self.predicted_df['RAM Frequency'].astype(int)
        self.predicted_df['Units Sold (millions)'] = self.predicted_df['Units Sold (millions)'].apply(integer_or_float_value)

        for column in ['Release Year', 'Launch Price', 'Number of Exclusives']:
            self.predicted_df[column] = self.predicted_df[column].astype(int)
        
        self.predicted_df['CPU Score'] = self.predicted_df['CPU Equivalent']
        self.predicted_df['GPU Score'] = self.predicted_df['GPU Equivalent']

        for index in range(len(self.predicted_df['GPU Equivalent'])):
            cpu_sub_score = 1000
            cpu_score = self.predicted_df.loc[index, 'CPU Equivalent']
            if cpu_score < 1.5:
                self.predicted_df.loc[index, 'CPU Equivalent'] = None
            else:
                for i in self.cpu_df.index:
                    if abs(self.cpu_df.loc[i, 'CPU Score'] - cpu_score) < cpu_sub_score:
                        cpu_sub_score = abs(self.cpu_df.loc[i, 'CPU Score'] - cpu_score)
                        index_cpu = i
                self.predicted_df.loc[index, 'CPU Equivalent'] = self.cpu_df.loc[index_cpu, 'Manufacturer'] + ' ' + self.cpu_df.loc[
                    index_cpu, 'Model']

            gpu_score = self.predicted_df.loc[index, 'GPU Equivalent']
            gpu_sub_score = 1000
            if gpu_score < 3:
                self.predicted_df.loc[index, 'GPU Equivalent'] = None
            else:
                for j in self.gpu_df.index:
                    if abs(self.gpu_df.loc[j, 'GPU Score'] - gpu_score) < gpu_sub_score:
                        gpu_sub_score = abs(self.gpu_df.loc[j, 'GPU Score'] - gpu_score)
                        index_gpu = j
                    self.predicted_df.loc[index, 'GPU Equivalent'] = self.gpu_df.loc[index_gpu, 'Manufacturer'] + ' ' + self.gpu_df.loc[
                        index_gpu, 'Model']


    def add_units_for_prediction_df(self, data_type = ''):
        if data_type == 'predicted':
            self.predicted_df = add_size_units_to_df_values(df=self.predicted_df, columns=['CPU Frequency', 'RAM Size', 'RAM Frequency'])
        elif data_type == 'original':
            self.original_df  = add_size_units_to_df_values(df=self.original_df , columns=['CPU Frequency', 'RAM Size', 'RAM Frequency'])


    def export_mse_to_file(self, remove_from_df_rows=[], output_path='./prediction.txt', merge_column='Release Year'):
        original_df_aux = self.original_df
        predicted_df_aux = self.predicted_df

        if len(remove_from_df_rows):
            for column, remove_list_values in remove_from_df_rows:
                original_df_aux = original_df_aux[~original_df_aux[column].isin(remove_list_values)]
                predicted_df_aux = predicted_df_aux[~predicted_df_aux[column].isin(remove_list_values)]

        original_df_aux = original_df_aux[original_df_aux[merge_column].isin(predicted_df_aux[merge_column].values)]
        original_df_aux = original_df_aux.sort_values(merge_column).reset_index(drop=True)
        predicted_df_aux = predicted_df_aux.sort_values(merge_column).reset_index(drop=True)

        mse_dict = {}
        mse_total = 0
        n = len(predicted_df_aux[merge_column].values)
        m = len(original_df_aux[merge_column].values)

        columns = ['CPU Frequency', 'RAM Size', 'RAM Frequency', 'Units Sold (millions)', 'Number of Exclusives', 'Launch Price', 'CPU Score', 'GPU Score']
        for column in columns:
                mse_i = 0
                nr = 0
                l = 0
                for i in range(0, n):
                    for j in range(l, m):
                        if predicted_df_aux.loc[i, merge_column] == original_df_aux.loc[j, merge_column]:
                            l += 1
                            nr += 1
                            mse_i += (predicted_df_aux.loc[i, column] - original_df_aux.loc[j, column]) ** 2
                        else:
                            break

                if nr != 0:
                    mse_i /= nr

                mse_dict[column] = mse_i
                mse_total += mse_i

        with open(output_path, 'w') as f:
            f.write('Column,MSE\n')
            for column, mse in mse_dict.items():
                f.write(f'{column},{mse}\n')
            f.write(f'\nTotal MSE={mse_total}\n')

            if self.linear_regressor_path:
                f.write(f'Linear Regression\n')

            if self.polynomial_regressor_path1:
                f.write(f'Polynomial Regression, Degree={self.poly_degree1}\n')

            if self.polynomial_regressor_path2:
                f.write(f'Polynomial Regression, Degree={self.poly_degree2}')


    def get_graphs(self, columns = ['CPU Frequency', 'RAM Size', 'RAM Frequency', 'Launch Price', 'Units Sold (millions)', 'Number of Exclusives'], merge_column='Release Year'):
        for column in columns:
            plt.figure()
            plt.plot(self.original_df[merge_column], self.original_df[column], 'bo', label='Actual')
            plt.plot(self.predicted_df[merge_column], self.predicted_df[column], 'r', label='Predicted')
            plt.legend(loc='best')
            plt.title(column)
            plt.xlabel(merge_column)
            plt.ylabel(column)
            plt.show()