from src.extract import read_parquet_files
from src.config import GOLD_PATH
import pandas as pd

#reading_all_gold_parquet_tables
gold_tables_parquet = read_parquet_files(GOLD_PATH)



# run code :
# python -m exploration_gold.validate_gold




# FACT_SALES VALIDATION

#DATA
fact_sales:pd.DataFrame = gold_tables_parquet['fact_sales']
dim_products:pd.DataFrame =gold_tables_parquet['dim_products']
dim_stores:pd.DataFrame =gold_tables_parquet['dim_stores']
dim_dates:pd.DataFrame =gold_tables_parquet['dim_date']


# 1 - how many rows and columns 
# print(fact_sales.shape)


# # 2 - which columns stay into a dataframe
# print(list(fact_sales.columns))


# # 3  - which data type have every column
# fact_sales.info()



# # 4 - Checking if have any null in to the dataframe
# print(fact_sales.isnull().sum())





#UNICITY AND DUPLICATES 

# run code :
# python -m exploration_gold.validate_gold




# 1 - Checking if a column sales_id contains duplicates
#rint(fact_sales['sale_id'].is_unique)


# 2 - Find Duplicate Rows
# find_duplicates:pd.DataFrame = fact_sales[fact_sales.duplicated()]
# print(find_duplicates)





#REFERENCIAL INTEGRITY

# 1 - fact sales and dim_products

#1.1 checkin all the product_id from fact_sales are in dim_products
# connection_exists_fact_sales_dim_products= fact_sales['product_id'].isin(dim_products['product_id'])
# qty_exists:int = connection_exists_fact_sales_dim_products.sum()
# print(qty_exists)


# #1.2 checkin all the product_id from fact_sales not are some register  in dim_products
# connection_not_exists_fact_sales_dim_products = ~connection_exists_fact_sales_dim_products
# qty_not_exists:int = connection_not_exists_fact_sales_dim_products.sum()
# print(qty_not_exists)





# 2 - fact sales and dim_stores

# #2.1 checkin all the store_id from fact_sales are in dim_stores
# connection_exists_fact_sales_dim_stores= fact_sales['store_id'].isin(dim_stores['store_id'])
# qty_exists_stores:int = connection_exists_fact_sales_dim_stores.sum()
# print(qty_exists_stores)


# #2.2 checkin all the store_id from fact_sales not are some register  in dim_stores 
# connection_not_exists_fact_sales_dim_stores = ~connection_exists_fact_sales_dim_stores
# qty_not_exists_stores:int = connection_not_exists_fact_sales_dim_stores.sum()
# print(qty_not_exists_stores)





# 3 - fact sales and dim_dates

#3.1 checkin all the dates from fact_sales are in dim_dates
# connection_exists_fact_sales_dim_dates= fact_sales['sale_date'].isin(dim_dates['date'])
# qty_exists_dates:int = connection_exists_fact_sales_dim_dates.sum()
# print(qty_exists_dates)


# #3.2 checkin all the dates from fact_sales not are some register  in dim_dates
# connection_not_exists_fact_sales_dim_dates = ~connection_exists_fact_sales_dim_dates
# qty_not_exists_dates:int = connection_not_exists_fact_sales_dim_dates.sum()
# print(qty_not_exists_dates)




# VALIDATING VALUE FIELDS 

# 1 - Checking negative value in quantity column
quantity_invalid_values:int =  (fact_sales['quantity']<=0).sum()
print(quantity_invalid_values)



# 2 - Checking unit_price
unit_price_brl_invalid_values:int =  (fact_sales['unit_price_brl']<=0).sum()
print(unit_price_brl_invalid_values)



# 3 - checking discount
discounts_invalid_values:int = ((fact_sales['discount_pct']<0) | (fact_sales['discount_pct']>1)).sum()
print(discounts_invalid_values)