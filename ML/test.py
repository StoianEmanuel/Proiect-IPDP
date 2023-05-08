from utils import get_scores, get_df, add_boost, fill_with_mean


db_path = './Data/gaming.sqlite'
db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND
     [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 10'''

# Transform string into float for CPU columns
Transform_col = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 
                    'System Memory Frequency', 'TDP']
df = get_df(db_path, db_query, Transform_col)
df['Boost Clock'] = add_boost(df, 'Boost Clock')
df['TDP'] = fill_with_mean(df, 'TDP')
df['Maximum Operating Temperature'] = fill_with_mean(df, 'Maximum Operating Temperature')

# Columns to be scaled
cols_to_scale = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Number of Cores', 'Number of Threads', 
                 'System Memory Frequency', 'Launch Price ($)']
cols_to_scale_rev = ['Process Size (nm)', 'TDP', 'Maximum Operating Temperature']
print(get_scores(df, cols_to_scale, cols_to_scale_rev), '\n\n\n')



db_query = '''SELECT * FROM GPU WHERE [Release Year] > 1985 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND
            [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND
            [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0'''

# Transform string into float for GPU columns
Transform_col   = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'Memory Size', 'TDP']
df = get_df(db_path, db_query, Transform_col)
df['Core Boost Clock'] = add_boost(df, 'Core Boost Clock')
df['TDP'] = fill_with_mean(df, 'TDP')

# Columns to be scaled
cols_to_scale = ['Transistors (millions)', 'Shading Units', 'Core Base Clock', 'Core Boost Clock', 'Memory Size', 'Memory Bandwidth', 'Memory Clock Speed (Effective)', 'Launch Price ($)']
cols_to_scale_rev = ['Process Size (nm)', 'TDP']
print(get_scores(df, cols_to_scale, cols_to_scale_rev))