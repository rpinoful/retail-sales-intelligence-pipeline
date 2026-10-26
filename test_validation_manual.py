import pandas as pd
from src.automated_validation_gold import validate_dim_products



# TESTING QUANTITY

# # case 1 - valid records
# valid_sales = pd.DataFrame({
#     "sale_id": [1001, 1002],
#     "quantity": [5, 3]
# })


# validate_fact_sales(valid_sales)
# print("Test 1 : Passed")




# #case 2 - invalid records 
# invalid_sales = pd.DataFrame({
#     "sale_id": [1003, 1004],
#     "quantity": [-8, 2]
# })




# try:
#     validate_fact_sales(invalid_sales)
    
# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("TEST 2: FAILED")
    




# # TESTING SALE_ID
# duplicated_dataframes = pd.DataFrame(
#     {
#     "sale_id" :[1001,1002,1002],
#     "quantity":[5,3,8]   
#     })


# try:
#     validate_fact_sales(duplicated_dataframes)

# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("Unexpected error")


# # TESTING SALE_ID_NULSS
# value_nulls_dataframes = pd.DataFrame(
#     {
#     "sale_id" :[1001,None,1002],
#     "quantity":[5,3,8]   
#     })


# try:
#     validate_fact_sales(value_nulls_dataframes)

# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("Unexpected error")




# TESTING UNIT PRICE 
# test_sales = pd.DataFrame({
#     "sale_id": [1001, 1002, 1003],
#     "quantity": [5, 3, 8],
#     "unit_price_brl": [12.50, -5.00, 20.00]
# })



# try:
#     validate_fact_sales(test_sales)

# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("Unexpected error")
    
    
    
    
    
    
    
    
    
# # # TESTING UNIT PRICE 
# # test_discount = pd.DataFrame({
# #     "sale_id": [1001, 1002, 1003],
# #     "product_id": [101,102,999],
# # })



# # try:
# #     validate_fact_sales(test_discount)

# # except ValueError as error:
# #     print(f"TEST 2: PASSED - {error}")
    
# # else:
# #     print("Unexpected error")
    
    
    
    
    
    


# # TEST SALES INTEGRITY - products
# test_sales_integrity = pd.DataFrame({
#     "sale_id": [1001, 1002, 1003],
#     "product_id": [101,102,999]
# })




# test_products_integrity = pd.DataFrame({
#     "product_id": [101,102,103],
#     "product_name" : ['Arroz','Leche','Café']
# })




# try:
#     validate_sales_products(test_sales_integrity,test_products_integrity)

# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("TEST FAILED - Expected ValueError")
    
    
    
    
    
# # TEST SALES INTEGRITY - stores
# test_sales_integrity = pd.DataFrame({
#     "sale_id": [1001, 1002, 1003],
#     "store_id": [1,2,4]
# })




# test_stores_integrity = pd.DataFrame({
#     "store_id": [1,2,3],
#     "store_name" : ['Loja Centro','Loja Fronteira','E-commerce']
# })




# try:
#     validate_sales_stores(test_sales_integrity,test_stores_integrity)

# except ValueError as error:
#     print(f"TEST 2: PASSED - {error}")
    
# else:
#     print("TEST FAILED - Expected ValueError")









# test_sales_dates = pd.DataFrame({
#     "sale_id": [1001, 1002, 1003],
#     "sale_date": pd.to_datetime([
#         "2026-10-20 14:30:00",
#         "2026-10-21 09:15:00",
#         "2026-10-25 18:45:00"
#     ])
# })

# test_dim_dates = pd.DataFrame({
#     "date": pd.to_datetime([
#         "2026-10-20",
#         "2026-10-21",
#         "2026-10-22"
#     ])
# })

# try:
#     validate_sales_dim_dates(test_sales_dates, test_dim_dates)

# except ValueError as error:
#     print(f"TEST PASSED - {error}")

# else:
#     print("TEST FAILED - Expected ValueError")





# # GROSS AMOUNT MEASURE - Checking
# df = pd.read_parquet("data/gold/fact_sales.parquet")

# expected_gross_amount = df['quantity']*df['unit_price_brl'] 


# #adding invalid register 
# df.loc[0, "gross_amount"] = 9999.99

# difference = (expected_gross_amount - df['gross_amount']).abs()

# invalid_mask = (difference) > 0.01

# quantity_values_outside_range = invalid_mask.sum()



# print(quantity_values_outside_range)




# testing entire validate_fact_sales 


# df_fact_sales = pd.read_parquet("data/gold/fact_sales.parquet")

# df_fact_sales.loc[0, "discount_amount"] = 9999.99


# try:
#     validate_fact_sales(df_fact_sales)
    

    
# except ValueError as error:
#     print( f"TEST PASSED {error}")


# else:
#     print("End test execution ✅")
    
    







# #testing entire validate_fact_sales adding outsider value (expected error)
# df_fact_sales = pd.read_parquet("data/gold/fact_sales.parquet")
# df_fact_sales.loc[0, "discount_amount"] = 9999.99
# test_2 = validate_fact_sales(df_fact_sales)
# print(test_2)



# DISCOUNT AMOUNT MEASURE- CHECKING 

# # 1 - reading parquet from data folder to test measure without logic 
# df_fact_sales = pd.read_parquet("data/gold/fact_sales.parquet")


# # #adding invalid register 
# df_fact_sales.loc[0, "discount_amount"] = 9999.99


# # 2 - recreating measure discount_amount (using series)
# expected_discount_amount = df_fact_sales['gross_amount']*df_fact_sales['discount_pct']



# # 3 - creating invalid mask for outsiders values between calculated column and original column
# invalid_mask_values_outsiders_da= ((expected_discount_amount -df_fact_sales['discount_amount']).abs())>0.01


# # 4 - quantity of outsiders
# quantity_values_outside_range = invalid_mask_values_outsiders_da.sum()


# print(quantity_values_outside_range)






# # NET AMOUNT MEASURE - CHECKING 

# df_fact_sales = pd.read_parquet("data/gold/fact_sales.parquet")

# try:
#     validate_fact_sales(df_fact_sales)
# except ValueError as error:
#     print( f"TEST PASSED {error}")



# else:
#     print("TEST PASSED - All validations successful ✅")   













# 2 - VALIDATE DIM PRODUCTS FUNCTION 


# # testing - duplicated checking

# df = pd.read_parquet("data/gold/dim_products.parquet")


# try:
#     validate_dim_products(df)
    
    
# except ValueError as error:
#     print( f"TEST PASSED {error}")



# else:
#     print("TEST PASSED - All validations successful ✅")   





# 2 - VALIDATE DIM PRODUCTS FUNCTION 


# testing- nulls values 

df = pd.read_parquet("data/gold/dim_products.parquet")






try:
    validate_dim_products(df)
    
    
except ValueError as error:
    print( f"TEST PASSED {error}")



else:
    print("TEST PASSED - All validations successful ✅")   
