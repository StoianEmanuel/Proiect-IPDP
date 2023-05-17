from joblib import load
from matplotlib import pyplot as plt
import pandas as pd
from utils import predicition, get_df, add_boost, remove_columns        #ML.utils


class Processor:
    def __init__(self,  year, columns, linear_regressor_file = None, lin_int_col = None, 
                 poly_regressor_file1 = None, poly_int_col1 = None, degree1 = None,
                 poly_regressor_file2 = None, poly_int_col2 = None, degree2 = None,
                 db_path = None, db_query = None, string_columns = None, reduce_size = True):
        self.year = year
        self.columns = columns

        if linear_regressor_file:
            self.linear_regressor = load(linear_regressor_file)
        else:
            self.linear_regressor = None
        
        if poly_regressor_file1:
            self.poly_regressor1  = load(poly_regressor_file1)
        else:
            self.poly_regressor1 = None
        
        if poly_regressor_file2:
            self.poly_regressor2  = load(poly_regressor_file2)
        else:
            self.poly_regressor2 = None

        self.lin_int_col = lin_int_col
        self.poly_int_col1 = poly_int_col1
        self.degree1 = degree1

        self.poly_int_col2 = poly_int_col2
        self.degree2 = degree2

        self.predicted_df = None

        if db_path and db_query:
            self.original_df = get_df(db_path, db_query, string_columns, None, None)
            if reduce_size:
                self.original_df = remove_columns(self.original_df, columns)
        else:
            self.original_df = pd.DataFrame()


    # Make predictions
    def read_data(self):

        self.predicted_df = predicition(release_year=self.year, columns=self.columns, 
                                        linear_regressor=self.linear_regressor, lin_int_col=self.lin_int_col,
                                        poly_regressor1 = self.poly_regressor1, poly_degree1 = self.degree1, poly_int_col1 = self.poly_int_col1,
                                        poly_regressor2 = self.poly_regressor2, poly_degree2 = self.degree2, poly_int_col2 = self.poly_int_col2)

    # Possibilty that i won't need 
    def get_df(self):
        return self.predicted_df


    # Print predicted or original (data from database)
    def print_data(self, data_type=''):
        if data_type == 'predicted':
            print('Predicted data:\n')
            for i in range(0, self.predicted_df.shape[1], 3):
                pd.options.display.max_rows = None
                print(self.predicted_df.iloc[:, i:i+3], '\n')

        elif data_type == 'original':
            print('Original data:\n')
            for i in range(0, self.original_df.shape[1], 3):
                pd.options.display.max_rows = None
                print(self.original_df.iloc[:, i:i+3], '\n')


    # Fill "Boost Clock" column of original dataframe with "Base Clock" where "Boost Clock" is ''
    def add_boost_clock(self, column):
        self.original_df[column] = add_boost(self.original_df, column)


    # Export mse value for prediction to 
    def export_mse_to_file(self, remove_from_df_rows = [], output_path = './predition.txt', merge_column = 'Release Year'):
        # Remove specified rows from original_df
        original_df_aux = self.original_df
        predicted_df_aux = self.predicted_df

        if len(remove_from_df_rows):
            for column, remove_list_values in remove_from_df_rows:
                original_df_aux = original_df_aux[~original_df_aux[column].isin(remove_list_values)]
                predicted_df_aux = predicted_df_aux[~predicted_df_aux[column].isin(remove_list_values)]
        
        # Remove data that will not be used and sort rows by merge_column values
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
                mse_dict[column] = mse_i
                mse_total += mse_i
        
        with open(output_path, 'w') as f:
            f.write('Column,MSE\n')
            for column, mse in mse_dict.items():
                f.write(f'{column}={mse}\n')
            f.write(f'\nTotal MSE={mse_total}\n')

            if self.linear_regressor:
                f.write(f'Linear Regression\n')
            
            if self.poly_regressor1:
                f.write(f'Polynomial Regression, Degree={self.degree1}\n')
            
            if self.poly_regressor2:
                f.write(f'Polynomial Regression, Degree={self.degree2}')
    

    # Display graphs for a set of columns with merge_column as X axis
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