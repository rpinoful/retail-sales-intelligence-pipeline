import pandas as pd
from src.automated_validation_gold import validate_sales_stores



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
    
    
    
    
    
# TEST SALES INTEGRITY - stores
test_sales_integrity = pd.DataFrame({
    "sale_id": [1001, 1002, 1003],
    "store_id": [1,2,4]
})




test_stores_integrity = pd.DataFrame({
    "store_id": [1,2,3],
    "store_name" : ['Loja Centro','Loja Fronteira','E-commerce']
})




try:
    validate_sales_stores(test_sales_integrity,test_stores_integrity)

except ValueError as error:
    print(f"TEST 2: PASSED - {error}")
    
else:
    print("TEST FAILED - Expected ValueError")