from utils import get_correlation, remove_columns, get_df, fill_with_mean, add_boost


# modify it for a proper corelation


main_key= ['Release Year']
other_keys = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature',
              'System Memory Frequency', 'TDP', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']
db_path = './Data/gaming.sqlite'
db_query = '''SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND
 [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0'''
keys = main_key + other_keys

df = get_df(db_path, db_query, keys)
df['Boost Clock'] = add_boost(df, 'Boost Clock')
df['TDP'] = fill_with_mean(df, 'TDP')
df['Maximum Operating Temperature'] = fill_with_mean(df, 'Maximum Operating Temperature')
df = remove_columns(df, keys)

print(main_key[0]+':\n', get_correlation(df, main_key = main_key[0], keys = other_keys))