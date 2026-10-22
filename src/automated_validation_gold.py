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