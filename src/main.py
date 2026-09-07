from pprint import pprint
from extract import read_excel,read_parquet_files
from validate import validate_all_columns
from config import REQUIRED_COLUMNS, RAW_EXCEL_PATH,BRONZE_PATH,SILVER_PATH,GOLD_PATH
from load import save_parquet
from transform import transform_all_dataframes_bronze
from model import build_gold_model


# Bronze Chapter
dataframes = read_excel(RAW_EXCEL_PATH)
validate_all_columns(dataframes,REQUIRED_COLUMNS)
save_parquet(dataframes,BRONZE_PATH)




#silver chapter

# 1 - Getting all the dataframes to clean
dataframes_bronze= read_parquet_files(BRONZE_PATH)


#2 - Transform all bronze dataframes
dataframes_silver = transform_all_dataframes_bronze(dataframes_bronze)

# 3 - Save dataframe_silver dictionary to parquet 
save_parquet(dataframes_silver,SILVER_PATH)




#GOLD CHAPTER 
dataframes_gold= build_gold_model(dataframes_silver,"2026-01-01","2026-12-31")
save_parquet(dataframes_gold,GOLD_PATH)