from extract import read_excel







route = 'data/raw/excel/store_operations.xlsx'
dataframes = read_excel(route)

for df_name,df_content in dataframes.items():
    print(f"The dataframe name is{df_name}\n")
    print(df_content.shape)


