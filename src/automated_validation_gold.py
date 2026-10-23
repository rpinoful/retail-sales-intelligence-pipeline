import pandas as pd


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
    




def validate_dim_products(df: pd.DataFrame):
    pass


def validate_dim_stores(df: pd.DataFrame):
    pass


def validate_fact_fixed_costs(df: pd.DataFrame):
    pass


def validate_dim_date(df: pd.DataFrame):
    pass








def validate_gold(dataframes_gold: dict[str, pd.DataFrame]):
    pass