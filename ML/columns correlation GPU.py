from utils import get_correlation, get_df_for_gpu, remove_columns

main_key= ['Memory Size']
other_keys = ['Core Base Clock', 'Core Boost Clock', 'Memory Clock Speed (Effective)', 'Memory Bandwidth', 'TDP', 'Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Launch Price ($)']
API_v1_col = ['DirectX', 'OpenGL']
API_v2_col = ['Shader Model', 'CUDA', 'OpenCL']
db_path = './Data/gaming.sqlite'
db_query = 'SELECT * FROM GPU WHERE [Release Year] > 1970 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0'
df = get_df_for_gpu(db_path, db_query, other_keys + main_key, API_v1_col, API_v2_col) 
df = remove_columns(df, other_keys + API_v2_col + API_v1_col + main_key)

print(main_key[0]+':\n', get_correlation(df, main_key = main_key[0], keys = other_keys + API_v2_col + API_v1_col))