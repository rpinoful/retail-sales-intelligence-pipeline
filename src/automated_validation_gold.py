import pandas as pd
from src.config import ALLOW_CATEGORIES,ALLOW_CURRENCIES_SUPPLIERS,VALIDATE_CHANNELS,FIXED_COST_COLUMNS,FIXED_COST_COMPONENT_COLUMNS

def validate_fact_sales(df: pd.DataFrame) -> None:
    
    # QUANTITY COLUMN 
    
    #1 - Creating invalid mask , to checking if exist invalid values in quantity column
    invalid_mask_quantity = (df['quantity']<=0) | (df['quantity'].isna())
    
    # 2 - Sum all the invalid rows 
    quantity_invalid_values = invalid_mask_quantity.sum()
    
    
    # 3 - Checking if exists invalid values , if return different to zero return error and stop the datapipeline
    if quantity_invalid_values !=0:
        raise ValueError(f"Found {quantity_invalid_values} invalid quantities")
    
    
    
    
    
    # SALE_ID COLUMN 
    
    # SALE_ID_DUPLICATES
    
    # 1 - Creating invalid mask to checking if exist duplicated values 
    invalid_mask_sale_id = df['sale_id'].duplicated()
    
    
    # 2 - Count all the ids duplicates from filter the dataframe with the mask 
    quantity_duplicates = invalid_mask_sale_id.sum()
    
    
    # 3 - 
    if quantity_duplicates !=0:
        raise ValueError(f"Found {quantity_duplicates} duplicated sale IDs")
    
    
    
    
    
    # SALE_ID COLUMN -PT-2 
        
    # SALE_ID_NULL_VALUES
        
    # 1 - Creating invalid mask to checking if exist duplicated values 
    invalid_mask_sale_id_nulls = df['sale_id'].isna()
        
        
    # 2 - Count all the nulls ids from filter the dataframe with the mask 
    quantity_nulls = invalid_mask_sale_id_nulls.sum()
        
        
    # 3 - 
    if quantity_nulls !=0:
        raise ValueError(f"Found {quantity_nulls} nulls sale IDs")
    


    #Unit_price_brl - column
    
    # 1 - invalid mask detecting invalid prices
    invalid_mask_unit_price_brl = (df['unit_price_brl']<=0) | (df['unit_price_brl'].isna())
    
    
    # 2 - count all the invalid prices from the mask 
    quantity_invalid_prices = invalid_mask_unit_price_brl.sum()
    
    if quantity_invalid_prices !=0:
            raise ValueError(f"Found {quantity_invalid_prices} invalid prices")
    
    
    
    
    # DISCOUNT_PCT COLUMN

    # 1 - Create invalid mask
    invalid_mask_pct = (~df['discount_pct'].between(0,1)) |(df['discount_pct'].isna())
    
    # 2 - Count invalid discounts
    quantity_invalid_discounts = invalid_mask_pct.sum()
    
    
    # 3 - Raise ValueError if invalid discounts exist
    if quantity_invalid_discounts !=0:
        raise ValueError(f"Found {quantity_invalid_discounts} invalid discounts")





    # measures about numeric values 


    #- Gross amount

    # 1 - recreating the calculate 
    expected_gross_amount = df['quantity']*df['unit_price_brl'] 
    
    # 2 - filtering gross_amount outstider using mask
    invalid_mask_values_outsiders_values_ga = ((expected_gross_amount - df['gross_amount']).abs())>0.01

    # 3 - Counting invalid values returned by the mask
    quantity_outsiders_gross_amount:int = invalid_mask_values_outsiders_values_ga.sum()


    # 4 - Raise value error if exists gross amount outside define rule
    if quantity_outsiders_gross_amount!=0:
        raise ValueError(f"Found {quantity_outsiders_gross_amount} invalid gross amount values")




    # Discount_amount

    # 1 - recreating measure discount_amount (using series)
    expected_discount_amount = df['gross_amount']*df['discount_pct']

    # 2 - creating invalid mask for outsiders values between calculated column and original column
    invalid_mask_values_outsiders_da=((expected_discount_amount -df['discount_amount']).abs())>0.01

    # 3 - quantity of outsiders
    quantity_values_outside_range = invalid_mask_values_outsiders_da.sum()


    # 4 - checking if exists outsiders from the calculate discount_amount
    if quantity_values_outside_range!=0:
        raise ValueError(f"Found {quantity_values_outside_range} invalid outside range values")
    
    
    
    
    # NET AMOUNT MEASURE - CHECKING 


    # 1 - Recreate the calculate of net_amount 
    # net_amount = gross_amount - discount_amount
    expected_net_amount = df['gross_amount']- df['discount_amount']



    # 2 - creating invalid mask for outsiders values between calculated column and original column , is necessary round 2 decimals because a minimun difference 
    invalid_mask_values_outsiders_na = (((expected_net_amount - df['net_amount']).abs()).round(2)) >0.01


    # 3 - quantity of outsiders 
    quantity_values_outside_range_na = invalid_mask_values_outsiders_na.sum()

    if quantity_values_outside_range_na!=0:
        raise ValueError(f"Found {quantity_values_outside_range_na} invalid outside range netamount values ")
    




def validate_sales_products(fact_sales: pd.DataFrame,dim_products: pd.DataFrame) -> None:
    # Referencial integrity
    
    # 1 - creating mask with a isin function and two common columns 
    invalid_referential_integrity = ~(fact_sales['product_id'].isin(dim_products['product_id']))
    
    #2 - Quantity of rows dataframes without integration
    quantity_products = invalid_referential_integrity.sum()
    
    
    # 3 - checking total 
    if quantity_products !=0:
        raise ValueError(f"Found {quantity_products} unregistered products")





def validate_sales_stores(fact_sales: pd.DataFrame,dim_stores: pd.DataFrame) -> None:
    # 1 - Creating mask with a isin function two column function and two common columns
    invalid_referential_integrity_sales_stores = ~(fact_sales['store_id'].isin(dim_stores['store_id']))

    
    
    # 2 - Quantity of rows dataframes without integration
    quantity_stores = invalid_referential_integrity_sales_stores.sum()


    #3 - checking total
    if quantity_stores!=0:
        raise ValueError(f"Found {quantity_stores} unregistered stores")








def validate_sales_dim_dates(fact_sales: pd.DataFrame,dim_dates: pd.DataFrame) -> None:
    
    # 1 - Normalize date froms fact_Sales 
    temp_fact_sales:pd.Series = fact_sales['sale_date'].dt.normalize()
    
    
    #2 - checking if each date into fact_sales exists into dim_dates
    invalid_mask_sales_date = ~(temp_fact_sales.isin(dim_dates['date']))
    
    
    # 3 - quantity
    qty_invalid_sales_date = invalid_mask_sales_date.sum()

    #4 - checking total
    if qty_invalid_sales_date!=0:
        raise ValueError(f"Found {qty_invalid_sales_date} unregistered dates")
    




def validate_dim_products(df: pd.DataFrame)->None:
    
    # 1 - Duplicated value product_id column 
    
    # Creating mask
    mask_duplicated_product_id = df['product_id'].duplicated()


    # quantity of duplicated values from the column product_id
    qty_duplicated_products_id = mask_duplicated_product_id.sum()


    # if exists duplicated values
    if qty_duplicated_products_id!=0:
        raise ValueError(f"Found {qty_duplicated_products_id} product id duplicated")
        
    
    
    
    
    
    # 2 - Null values in product_id column
    mask_nulls_product_id = df['product_id'].isna()
    
    
    # quantity of duplicated values from the column product_id
    qty_nulls_products_id = mask_nulls_product_id.sum()
    
    
        # if exists duplicated values
    if qty_nulls_products_id!=0:
        raise ValueError(f"Found {qty_nulls_products_id} product id Null values")
            
    
    
    
    
    # 3 - Unit_cost validate 
    
    # 1 - creating mask to filter invalid costs from unit_cost_brl dim_products
    mask_invalid_costs_products = (df['unit_cost'] <=0) | (df['unit_cost'].isna())
    
    
    
    # 2 - How many null values was found into the cost column
    qty_invalid_costs = mask_invalid_costs_products.sum()
    
    
    
    
    #3 - Forcing error if exist some invalid cost
    if qty_invalid_costs:
        raise ValueError(f"Found {qty_invalid_costs} invalid costs values")
    
    
    
    
    
    # 4 - register categories 
    
    # 1 - creating mask to filter invalid costs from unit_cost_brl dim_products
    mask_invalid_categories_products = ~(df['category'].isin(ALLOW_CATEGORIES))
        
        
        
    # 2 - How many null values was found into the cost column
    qty_invalid_categories = mask_invalid_categories_products.sum()
        
        
        
        
    #3 - Forcing error if exist some invalid cost
    if qty_invalid_categories:
        raise ValueError(f"Found {qty_invalid_categories} invalid categories")
    
    
    
    
    #5 - product_name - nullls or empty
    invalid_mask_product_name = (df['product_name'].isna()) | (df['product_name'].str.strip().eq(""))
    
    
    qty_invalid_product_names = invalid_mask_product_name.sum()
    
    
    
    if qty_invalid_product_names:
        raise ValueError(f"Found {qty_invalid_product_names} invalid product_names")
    
    
    
    
            
    
    
    # 5 - Registered currencies
    
    # 1 - creating mask to filter invalid costs from unit_cost_brl dim_products
    mask_invalid_currencies = ~(df['supplier_currency'].str.strip().str.upper().isin(ALLOW_CURRENCIES_SUPPLIERS))
            
            
            
    # 2 - How many null values was found into the cost column
    qty_invalid_currencies = mask_invalid_currencies.sum()
            
            
            
            
    #3 - Forcing error if exist some invalid cost
    if qty_invalid_currencies:
        raise ValueError(f"Found {qty_invalid_currencies} invalid supplier_currencies")
        
    
    
    
    
    
    # 6 - Active 
    
    #1 - creating invalid mask , not boolean and not nulls
    #invalid_mask_active_product =  (df["active"].dtype!=bool) | (df["active"].isna())
    
    invalid_mask_active_product = ~(df["active"].map(lambda bool_values: isinstance(bool_values,bool)))

    # 2 - quantity of invalid values from the column active
    qty_invalid_active_values = invalid_mask_active_product.sum()
    
    
    
    
    # 3 - quantity of invalid or nulls values from active column
    if qty_invalid_active_values:
        raise ValueError(f"Found {qty_invalid_active_values} not boolean values or null values in the column")

        
    
    




def validate_dim_stores(df: pd.DataFrame):
    
    # 1 - checking duplicate id_stores
    mask_duplicate_stores_id = df['store_id'].duplicated() 
    
    qty_duplicates_stores_id = mask_duplicate_stores_id.sum()
    
    if qty_duplicates_stores_id:
        raise ValueError(f"Found {qty_duplicates_stores_id} duplicated values in the column store_id")
    
    
    
    
    
    
    
    # 2 - checking nulls id_stores
    mask_nulls_stores_id = df['store_id'].isna()
        
    qty_nulls_stores_id = mask_nulls_stores_id.sum()
        
    if qty_nulls_stores_id:
        raise ValueError(f"Found {qty_nulls_stores_id} null values in the column store_id")
    
    
    
    
    
    
    
    
    # 3 -  checking columns strings empty or only contains spaces
    mask_invalid_channel = ~(df['channel'].isin(VALIDATE_CHANNELS))
    
    qty_invalid_channel = mask_invalid_channel.sum()
    
    
    if qty_invalid_channel:
        raise ValueError(f"Found {qty_invalid_channel} invalid channels")
    
    
    result_empty = check_empty_strings(df)

    for column, num_empty in result_empty.items():
        if num_empty:
            raise ValueError(
                f"Column:{column} - empty values:{num_empty}"
            )
    



    result_nulls = check_nulls_strings(df)

    for column, num_nulls in result_nulls.items():
        if num_nulls:
            raise ValueError(
                f"Column:{column} - nulls values:{num_nulls}"
            )
    
  
    







def validate_fact_fixed_costs_stores(df1: pd.DataFrame,df2: pd.DataFrame)->None:

    # 1- Creating the mask
    mask_integrity_fixed_costs_stores = ~(df1['store_id'].isin(df2['store_id']))

    # 2 - how many rows contains without referencial intregity
    qty_invalid_stores_integrity = mask_integrity_fixed_costs_stores.sum()

    # 3 - 
    if qty_invalid_stores_integrity:
        raise ValueError(f"Found {qty_invalid_stores_integrity} IDs in fact_fixed_costs missing from dim_stores")






def validate_fact_fixed_costs(df: pd.DataFrame):

    #- duplicity

    # 1 - creating a mask 
    mask_duplicated_store_month= df.duplicated(subset=['store_id','start_month'])

    #2 - qty of month rent duplicated
    qty_duplicated_store_month = mask_duplicated_store_month.sum()

    #3  - 
    if qty_duplicated_store_month:
        raise ValueError(f"Found {qty_duplicated_store_month} duplicated store_id/start_month combinations")




    # invalid values column rent_brl
    mask_invalid_rent_brl = (df['rent_brl']<0) | (df['rent_brl'].isna())
    
    
    
    qty_invalid_rent_brl = mask_invalid_rent_brl.sum()


    if qty_invalid_rent_brl:
        raise ValueError(f"Found {qty_invalid_rent_brl} negative or null values in rent_brl")



    #invalid numeric values
    results_invalid_numeric_values = check_invalid_numeric_values(df,FIXED_COST_COLUMNS)

    for numeric_column,value in results_invalid_numeric_values.items():
        if value:
            raise ValueError(f"Column:{numeric_column} - invalid values: {value}")



    #validating start_month

    # 1 - taking a day from dataframe using dt , and making a mask throght it 
    mask_invalid_dates = ~(df['start_month'].dt.is_month_start)


    #2 - quantify invald dates
    qty_invalid_start_month = mask_invalid_dates.sum()


    # 3 - checking if exists invalid dates and returning value error 
    if qty_invalid_start_month:
        raise ValueError(f"Found {qty_invalid_start_month} invalid or null dates in start_month")




    # Validation total_fixed_cost_brl 

    # 4 - Checking if  total_fixed_cost_brl is a sum of four columns in to the dataframe
    total_fixed_cost_sum_check:pd.Series= df[FIXED_COST_COMPONENT_COLUMNS].sum(axis=1)

    mask_total_fixed_costs = ((((df['total_fixed_cost_brl'] - total_fixed_cost_sum_check).round(2)).abs())>0.01)

    qty_total_outside_range = mask_total_fixed_costs.sum()


    if qty_total_outside_range:
        raise ValueError(f"Found {qty_total_outside_range} total fixed costs outside range")

    










def validate_dim_date(df: pd.DataFrame):
    pass








def validate_gold(dataframes_gold: dict[str, pd.DataFrame]):
    pass






# AUX FUNCTIONS 


def check_empty_strings(df:pd.DataFrame) -> dict :
    resultado ={}
    string_columns = df.select_dtypes(include='string').columns
    
    for column in string_columns:
        num_char_columns = df[column].str.strip().str.len().eq(0).sum()
        resultado[column] = num_char_columns
    
    return resultado




def check_nulls_strings(df: pd.DataFrame) -> dict:
    result = {}
    string_columns = df.select_dtypes(include='string').columns

    for column in string_columns:
        nulls_values_column = df[column].isna().sum()
        result[column] = nulls_values_column

    return result




def check_invalid_numeric_values(df: pd.DataFrame,numeric_columns:list) -> dict:
    result = {}

    for column in numeric_columns:
        invalid_values_numeric_column = ((df[column]<0) | (df[column].isna())).sum()
        result[column] = invalid_values_numeric_column

    return result





def check_physical_stores_zero_rent(df_fixed_costs: pd.DataFrame,df_stores: pd.DataFrame) -> pd.DataFrame:

    #1- Filtering - fisicas stores
    df_stores_fisica = df_stores.loc[df_stores['channel']=='Física']


    #2 - Filtering df_fixed_costs with rent_brl equals to zero
    df_fixed_costs_rent_brl_0 = df_fixed_costs.loc[df_fixed_costs['rent_brl']== 0]


    # 3 - merge the dataframe results after it filtering
    df_result = pd.merge(df_stores_fisica,df_fixed_costs_rent_brl_0,on='store_id',how='inner')


    return df_result








