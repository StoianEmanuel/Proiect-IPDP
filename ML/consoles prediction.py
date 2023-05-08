import pandas as pd
from utils import add_boost, fill_with_mean, get_df


# Get data from Consoles table
db_path = './Data/gaming.sqlite'
console_query = '''SELECT Name AS [Consoles Name], [Release Year], [Units Sold (millions)], [Number of Exclusives],
 [CPU Equivalent] AS [CPU Name], [CPU Frequency] AS [Base Clock], [GPU Equivalent] AS [GPU Name], [RAM Size], [RAM Frequency], 
 [Launch Price ($)] AS [Launch Price] FROM Consoles'''

transform_columns = ['Base Clock', 'RAM Size', 'RAM Frequency', 'Launch Price']
console_df = get_df(db_path = db_path, db_query = console_query, keys = transform_columns)


# Get data from CPU table
cpu_query = '''SELECT Model, Manufacturer, [Base Clock], [Boost Clock], [L1 Cache Size], [L2 Cache Size], [Number of Cores], 
 [Number of Threads], [System Memory Frequency], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size], 
 TDP, [Maximum Operating Temperature] FROM CPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 
                        'System Memory Frequency', 'TDP']
cpu_df = get_df(db_path = db_path, db_query = cpu_query, keys = transform_columns)

cpu_df['Boost Clock'] = add_boost(cpu_df, 'Boost Clock')
cpu_df['TDP'] = fill_with_mean(cpu_df, 'TDP')
cpu_df['Maximum Operating Temperature'] = fill_with_mean(cpu_df, 'Maximum Operating Temperature')

# Get data from GPU table
gpu_query = '''SELECT Model, Manufacturer, [Core Base Clock] AS [Base Clock], [Core Boost Clock] AS [Boost Clock],
 [Shading Units], [Transistors (millions)], [Memory Size], [Launch Price ($)] AS [Launch Price], [Process Size (nm)] AS [Process Size],
 TDP, [Memory Bandwidth], [Memory Clock Speed (Effective)] AS [Memory Clock Speed] FROM GPU'''

transform_columns = ['Base Clock', 'Boost Clock', 'Memory Size', 'Launch Price', 'TDP', 'Memory Bandwidth', 'Memory Clock Speed']
gpu_df = get_df(db_path = db_path, db_query = gpu_query, keys = transform_columns)

gpu_df['Boost Clock'] = add_boost(gpu_df, 'Boost Clock')
gpu_df['TDP'] = fill_with_mean(gpu_df, 'TDP')

# Extract data from CPU and GPU tables for cpu and gpu used in consoles from Consoles table
"""
console_df  = pd.read_sql_query(f'''
SELECT Consoles.Name AS [Consoles Name], Consoles.[Release Year] AS [Release Year Consoles], Consoles.[Units Sold (millions)],
 Consoles.[Number of Exclusives], Consoles.[RAM Size], Consoles.[RAM Frequency], Consoles.[Launch Price ($)] AS [Launch Price Consoles],
 CPU.[Base Clock] AS [Base Clock CPU], CPU.[Boost Clock] AS [Boost Clock CPU], CPU.[L1 Cache Size], CPU.[L2 Cache Size],
 CPU.[Number of Cores], CPU.[Number of Threads], CPU.[System Memory Frequency], CPU.[Launch Price ($)] AS [Launch Price CPU],
 CPU.[Process Size (nm)] AS [Process size CPU], CPU.[TDP] AS [TDP CPU], CPU.[Maximum Operating Temperature],
 GPU.[Transistors (millions)] AS [Transistors (millions) GPU], GPU.[Shading Units], GPU.[Core Base Clock] AS [Base Clock GPU],
 GPU.[Core Boost Clock] AS [GPU Boost Clock], GPU.[Memory Size] AS [Memory Size GPU], GPU.[Memory Bandwidth],
 GPU.[Memory Clock Speed (Effective)] AS [Memory Clock Speed GPU], GPU.[Launch Price ($)] AS [Launch Price GPU], 
 GPU.[Process Size (nm)] AS [Process size GPU], GPU.[TDP] AS [TDP GPU]
 FROM Consoles JOIN CPU ON substr(Consoles.[CPU Equivalent], 1, instr(Consoles.[CPU Equivalent], ' ')-1) = CPU.Manufacturer AND
 substr(Consoles.[CPU Equivalent], instr(Consoles.[CPU Equivalent], ' ')+1) = CPU.Model
 JOIN GPU ON substr(Consoles.[GPU Equivalent], 1, instr(Consoles.[GPU Equivalent], ' ')-1) = GPU.Manufacturer AND
 substr(Consoles.[GPU Equivalent], instr(Consoles.[GPU Equivalent], ' ')+1) = GPU.Model
''', conn)
"""

# Close connection

for i in range(0, console_df.shape[1], 3):
    pd.options.display.max_rows = None
    print(console_df.iloc[:, i:i+3])

'''# Columns to be scaled for CPU equivalent
scalable_columns_cpu = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads',
                         'System Memory Frequency', 'Launch Price ($)']
scalable_columns_rev_cpu = ['Process Size (nm)', 'TDP', 'Maximum Operating Temperature']

# Columns to be scaled for GPU equivalent
scalable_columns_gpu = ['Transistors (millions)', 'Shading Units', 'Core Base Clock', 'Core Boost Clock', 'Memory Size',
                         'Memory Bandwidth', 'Memory Clock Speed (Effective)', 'Launch Price ($)']
scalable_columns_rev_gpu = ['Process Size (nm)', 'TDP']

keys = scalable_columns_cpu + scalable_columns_rev_cpu + scalable_columns_gpu + scalable_columns_rev_gpu

for column in chain(keys):
        console_df[column].fillna("0", inplace=True)    # Fill empty values ("") with 0
        if console_df[column].dtype == object:
            console_df[column] = test_and_update(column, console_df[column])

console_df['Boost Clock'] = add_boost(console_df, 'Boost Clock')
console_df['Core Boost Clock'] = add_boost(console_df, 'Core Boost Clock')
console_df['TDP'] = fill_with_mean(console_df, 'TDP')
console_df['Maximum Operating Temperature'] = fill_with_mean(console_df, 'Maximum Operating Temperature')

console_df['CPU Score'] = get_scores_cpu(console_df, scalable_columns = scalable_columns_cpu,
                                          scalable_columns_rev = scalable_columns_rev_cpu)

console_df['GPU Score'] = get_scores_gpu(console_df, scalable_columns = scalable_columns_gpu,
                                          scalable_columns_rev = scalable_columns_rev_gpu )
print(console_df)
'''
