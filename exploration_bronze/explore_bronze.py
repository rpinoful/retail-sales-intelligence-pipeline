import pandas as pd
from src.extract import read_parquet_files
from src.config import BRONZE_PATH
from src.transform import transform_stores,transform_products,transform_fixed_costs

bronze_dataframes:dict[str, pd.DataFrame] = read_parquet_files(BRONZE_PATH)


# python -m exploration_bronze.explore_bronze

####################### SALES TABLE #############################################
# sales = bronze_dataframes['sales'].copy()
# # gross_amount (Total general , Total geral)

# sales['gross_amount'] = sales['quantity'] * sales['unit_price_brl']

# # discount_amount (Descuento total general , desconto Total geral)
# sales['discount_amount'] = (sales['gross_amount']* sales['discount_pct'])



# #net_amount (Total con descuento incluido , Total geral com desconto incluso)
# sales['net_amount'] = sales['gross_amount'] - sales['discount_amount'] 


# # round all the columns from entire dataframes
# sales = sales.round(2)




####################### STORE TABLE #############################################
# python -m exploration_bronze.explore_bronze


# # Testing function 
# stores = bronze_dataframes['stores']
# stores_silver_df = transform_stores(stores)
# print(stores_silver_df.to_string())




############ PRODUCTS TABLE #######################
# python -m exploration_bronze.explore_bronze
# products = bronze_dataframes['products'].copy()
# products_silver = transform_products(products)
# print(products_silver.to_string())




######## FIXED COSTS ###########################
# python -m exploration_bronze.explore_bronze

# duplicates_between_date_store:int= fixed_costs.duplicated(subset=['start_month','store_id']).sum()
#fixed_costs_numbers = fixed_costs.select_dtypes(include= 'number')
#fixed_costs_negative:pd.DataFrame= fixed_costs_numbers.loc[:,(fixed_costs_numbers <0).any()]

# print(fixed_costs.to_string())
# #print(fixed_costs_negative)
# print((fixed_costs_numbers <0).any())
# print(duplicates_between_date_store)

fixed_costs:pd.DataFrame = bronze_dataframes['fixed_costs'].copy()
transform_fixed_costs(fixed_costs)









  