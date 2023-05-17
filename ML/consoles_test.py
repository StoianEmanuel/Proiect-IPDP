from joblib import load
from utils import predicition, get_scores, add_boost, get_df, fill_column_with_mean_value, add_size_units_to_df_values


# Make predictions for consoles for values in year
def consoles_prediction(years = [], database_path = '', linear_regressor_path = None,
                         polynomial_regressor_path1 = None, poly_degree1 = None,
                         polynomial_regressor_path2 = None, poly_degree2 = None):
    
    # Load linear regression model and polynomial regression models
    linear_regressor = load(linear_regressor_path)
    poly_regressor1 = load(polynomial_regressor_path1)
    poly_regressor2 = load(polynomial_regressor_path2)

    columns = ['Release Year', 'Base Clock', 'RAM Size', 'RAM Frequency', 'CPU Equivalent', 'GPU Equivalent', 'Number of Exclusives',
                'Units Sold (millions)', 'Launch Price ($)']

    # Specify columns that will be transformed into int
    poly_int_col2 = [0, 1, 2]

    console_df = predicition(release_year = years, columns = columns, linear_regressor = linear_regressor, lin_int_col = None, 
                             poly_regressor1 = poly_regressor1, poly_degree1 = poly_degree1, poly_int_col1 = None, 
                             poly_regressor2 = poly_regressor2, poly_degree2 = poly_degree2, poly_int_col2 = poly_int_col2, 
                             )      
                                                                                                                                                
    console_df['RAM Size'] *= 0.55
    console_df['RAM Frequency'] *= 1000

    for column in ['Release Year', 'Launch Price ($)', 'Number of Exclusives']:
        console_df[column] = console_df[column].astype(int)

    add_size_units_to_df_values(df = console_df, columns = ['Base Clock', 'RAM Size', 'RAM Frequency'])

    # Get data from CPU table
    db_path = database_path
    cpu_query = '''SELECT Model, Manufacturer, [Release Year], [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
    [Number of Threads], [System Memory Frequency], [Launch Price ($)], [Process Size (nm)] AS [Process Size] FROM CPU'''

    transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'System Memory Frequency']
    cpu_df = get_df(db_path = db_path, db_query = cpu_query, keys = transform_columns)

    cpu_df['Boost Clock'] = add_boost(cpu_df, 'Boost Clock')
    cpu_df['Base Clock'] *= 5
    cpu_df['Boost Clock'] *= 7.5
    cpu_df['Process Size'] *= 0.1
    cpu_df['L2 Cache Size'] *= 5
    cpu_df['L1 Cache Size'] *= 4
    cpu_df['Number of Threads'] *= 2
    cpu_df['Number of Cores'] *= 2.5
    cpu_df['System Memory Frequency'] *= 10000


    # Get data from GPU table
    gpu_query = '''SELECT Model, Manufacturer, [Release Year], [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
    [Shading Units], [Transistors (millions)], [Memory Size], [Process Size (nm)] AS [Process Size],
    [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed], [Integration Density] FROM GPU'''

    transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth', 'Memory Clock Speed', 
                         'Integration Density']
    gpu_df = get_df(db_path = db_path, db_query = gpu_query, keys = transform_columns)
    gpu_df['Transistors (millions)'] *= 1000000
    gpu_df['Boost Clock'] = add_boost(gpu_df, 'Boost Clock')
    gpu_df['Boost Clock'] *= 1.1 

    # Change 0 value to mean value for 'Process Size' and 'Integration Density' column in gpu_df dataframe
    gpu_df['Process Size'] = fill_column_with_mean_value(df = gpu_df, column = 'Process Size', interval_columns = ['Release Year'],
        cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']],
                ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])['Process Size']

    gpu_df['Integration Density'] = fill_column_with_mean_value(df = gpu_df, column = 'Integration Density', interval_columns = ['Release Year'],
        cases = [['Manufacturer', ['Qualcomm', 'Imagination Technologies', 'Apple']], ['Manufacturer', ['AMD']],
                ['Manufacturer', ['Intel']], ['Manufacturer', ['NVIDIA']], ['Manufacturer', ['ATI', '3dfx']]])['Integration Density']


    # Store CPU and GPU Score into 'CPU Score' and 'GPU Score' columns in cpu_df and gpu_df dataframes
    cols_n_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 
            'System Memory Frequency']
    cpu_df['CPU Score'] = get_scores(cpu_df, scalable_columns = cols_n_cpu, scalable_columns_rev = None)

    cols_n_gpu = ['Transistors (millions)', 'Shading Units', 'Base Clock', 'Boost Clock', 'Memory Size', 'Memory Bandwidth',
                    'Memory Clock Speed', 'Integration Density']
    cols_rev_gpu = ['Process Size']
    gpu_df['GPU Score'] = get_scores(gpu_df, scalable_columns = cols_n_gpu, scalable_columns_rev = cols_rev_gpu)


    # Find CPU and GPU Equivalent predicted values for consoles
    for index in range(len(console_df['GPU Equivalent'])):
        cpu_sub_score = 1000
        cpu_score = console_df.loc[index, 'CPU Equivalent']
        if cpu_score < 1.5:
            console_df.loc[index, 'CPU Equivalent'] = None
        else:
            for i in cpu_df.index:
                if abs(cpu_df.loc[i, 'CPU Score'] - cpu_score) < cpu_sub_score:
                    cpu_sub_score = abs(cpu_df.loc[i, 'CPU Score'] - cpu_score)
                    index_cpu = i
            console_df.loc[index, 'CPU Equivalent'] = cpu_df.loc[index_cpu, 'Manufacturer'] + ' ' + cpu_df.loc[index_cpu, 'Model']


        gpu_score = console_df.loc[index, 'GPU Equivalent']
        gpu_sub_score = 1000
        if gpu_score < 3:
            console_df.loc[index, 'GPU Equivalent'] = None
        else:
            for j in gpu_df.index:
                if abs(gpu_df.loc[j, 'GPU Score'] - gpu_score) < gpu_sub_score:
                    gpu_sub_score = abs(gpu_df.loc[j, 'GPU Score'] - gpu_score)
                    index_gpu = j
                console_df.loc[index, 'GPU Equivalent'] = gpu_df.loc[index_gpu, 'Manufacturer'] + ' ' + gpu_df.loc[index_gpu, 'Model']


    # Print sets of 3 columns from dataframe
    '''for i in range(0, console_df.shape[1], 3):
        pd.options.display.max_rows = None
        print('\n', console_df.iloc[:, i:i+3])'''

    return console_df

'''df = consoles_prediction(years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023], database_path = './Data/gaming.sqlite',
                        linear_regressor_path = './ML/consoles_linear_regressor.joblib',
                        polynomial_regressor_path1 = './ML/consoles_poly_regressor1.joblib', poly_degree1 = 2, 
                        polynomial_regressor_path2 = './ML/consoles_poly_regressor2.joblib', poly_degree2 = 7)'''