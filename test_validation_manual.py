from asyncio.windows_events import NULL

import pandas as pd
from src.automated_validation_gold import validate_fact_sales



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
test_sales = pd.DataFrame({
    "sale_id": [1001, 1002, 1003],
    "quantity": [5, 3, 8],
    "unit_price_brl": [12.50, -5.00, 20.00]
})



try:
    validate_fact_sales(test_sales)

except ValueError as error:
    print(f"TEST 2: PASSED - {error}")
    
else:
    print("Unexpected error")