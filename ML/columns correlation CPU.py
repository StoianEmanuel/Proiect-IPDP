from utils import get_correlation, get_scores_cpu, remove_columns, get_df_for_cpu

main_key= ['Release Year']
other_keys = ['Base Clock', 'Boost Clock', 'L1 Cache Size', 'L2 Cache Size', 'Maximum Operating Temperature', 'System Memory Frequency', 'TDP', 'Number of Cores', 'Number of Threads', 'Process Size (nm)', 'Launch Price ($)']
db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM CPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Base Clock] IS NOT NULL AND [L1 Cache Size] IS NOT NULL AND [System Memory Frequency] IS NOT NULL AND [Number of Cores] > 0 AND [Launch Price ($)] > 0'
keys = main_key + other_keys

df = get_df_for_cpu(db_path, db_query, keys)
df = remove_columns(df, keys)

print(main_key[0]+':\n', get_correlation(df, main_key = main_key[0], keys = other_keys))
get_scores_cpu(df)