from pprint import pprint

from extract import read_excel

route = 'data/raw/excel/store_operations.xlsx'
dataframes = read_excel(route)



df_store = dataframes['stores']
df_online_empty = (df_store['state'].isna()) &  (df_store['channel']=='Online')

print(df_store)
print(df_online_empty)



