from predictions import Processor
from utils import add_size_units_to_df_values


# Call methods for CPU predictions of Processor class
def prediction_cpu(years = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030]):
    cpu_processor = Processor (year = years,
                    linear_regressor_file = './ML/CPU_linear_regressor.joblib',
                    lin_int_col = [0, 1],

                    poly_regressor_file1 = './ML/CPU_poly_regressor.joblib',
                    poly_int_col1 = [0, 1, 2, 3],
                    degree1 = 10,
                    
                    columns = ['Release Year', 'Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                        'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'],
                    
                    db_path = './Data/gaming.sqlite',
                    db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND
                                 [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND
                                 [Launch Price ($)] > 0 AND [Maximum Operating Temperature] IS NOT NULL AND [TDP] IS NOT NULL''',

                    string_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
                    'System Memory Frequency', 'TDP'])
    
    cpu_processor.read_data()

    cpu_processor.add_boost_clock('Boost Clock')

    cpu_processor.get_graphs(['Process Size (nm)', 'TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                       'Maximum Operating Temperature', 'Number of Cores', 'Number of Threads', 'System Memory Frequency', 'Launch Price ($)'])
    
    cpu_processor.export_mse_to_file(output_path = './ML/predition_cpu.txt', merge_column = 'Release Year')

    cpu_processor.predicted_df = add_size_units_to_df_values(cpu_processor.predicted_df, columns = ['TDP', 'Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size',
                    'Maximum Operating Temperature', 'System Memory Frequency'])
    
    cpu_processor.print_data('predicted')


# Call methods for GPU predictions of Processor class
def prediction_gpu(years = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030]):
    gpu_processor = Processor (year = years,
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
    
    gpu_processor.read_data()

    gpu_processor.add_boost_clock('Core Boost Clock')
    
    gpu_processor.get_graphs(['Transistors (millions)', 'Process Size (nm)', 'TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Shading Units', 'Memory Clock Speed (Effective)', 'Launch Price ($)'])
    
    gpu_processor.export_mse_to_file(output_path = './ML/predition_gpu.txt', merge_column = 'Release Year')

    gpu_processor.predicted_df = add_size_units_to_df_values(gpu_processor.predicted_df, columns = ['TDP', 'Core Base Clock', 'Core Boost Clock',
            'Memory Bandwidth', 'Memory Size', 'Integration Density', 'Memory Clock Speed (Effective)'])
    
    gpu_processor.print_data('predicted')


prediction_cpu()
prediction_gpu()