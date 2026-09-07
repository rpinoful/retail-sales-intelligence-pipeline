from src.extract import read_parquet_files
from src.config import GOLD_PATH
import pandas as pd

#reading_all_gold_parquet_tables
gold_tables_parquet = read_parquet_files(GOLD_PATH)



# run code :
# python -m exploration_gold.validate_gold




# FACT_SALES VALIDATION
fact_sales:pd.DataFrame = gold_tables_parquet['fact_sales']


# 1 - how many rows and columns 
print(fact_sales.shape)


# 2 - which columns stay into a dataframe
print(list(fact_sales.columns))


# 3  - which data type have every column
fact_sales.info()



# 4 - Checking if have any null in to the dataframe
print(fact_sales.isnull().sum())