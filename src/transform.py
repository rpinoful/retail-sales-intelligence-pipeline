import pandas as pd



def transform_sales(dataframe_sales:pd.DataFrame)-> pd.DataFrame:
    sales:pd.DataFrame = dataframe_sales.copy()

    # gross_amount (Total general , Total geral)
    sales['gross_amount'] = sales['quantity'] * sales['unit_price_brl']



    # discount_amount (Descuento total general , desconto Total geral)
    sales['discount_amount'] = (sales['gross_amount']* sales['discount_pct'])



    #net_amount (Total con descuento incluido , Total geral com desconto incluso)
    sales['net_amount'] = sales['gross_amount'] - sales['discount_amount'] 


    # round  the columns 
    columns =['net_amount','discount_amount','gross_amount','unit_price_brl']
    sales[columns] = sales[columns].round(2)

    return sales



def transform_stores(dataframe_stores:pd.DataFrame)-> pd.DataFrame:
    store:pd.DataFrame = dataframe_stores.copy()
    store.loc[
        (store['store_name']== 'E-commerce') & (store['city']== 'Online'),
        "state"
    ] = 'N/A'
    return store



def transform_products(dataframe_products:pd.DataFrame)-> pd.DataFrame:
    products:pd.DataFrame = dataframe_products.copy()
    products = products.rename(columns={'unit_cost_brl':'unit_cost'})
    return products



def transform_fixed_costs(dataframe_fixed_costs:pd.DataFrame)-> pd.DataFrame:
    fixed_costs:pd.DataFrame = dataframe_fixed_costs.copy()
    fixed_costs= fixed_costs.astype({'rent_brl': float, 'payroll_brl': float,'utilities_brl':float,'other_costs_brl':float})
    fixed_costs = fixed_costs.rename(columns={'month':'start_month'})
    print(f" Was transform the dataframe  fixed_cost with sucess ✅")
    return fixed_costs







def transform_all_dataframes_bronze(dataframe: dict[str, pd.DataFrame])->dict[str, pd.DataFrame] :
    """
    1 - Received a dataframe dictionary
    2 - Looping the dataframe
    3 - Each dataframe taking is pass to support dictionary to take a transform function , and the dataframe it is send to transform
    """
    silver_dataframe_dictionary:dict = {}



    #iterate dictionary dataframe
    for table_name,df in dataframe.items():
        transform_function:function = transformers[table_name]
        df_silver:pd.DataFrame =transform_function(df)
        silver_dataframe_dictionary[table_name]:dict[str, pd.DataFrame]= df_silver


    return silver_dataframe_dictionary






transformers = {
    "sales": transform_sales,
    "stores" :transform_stores,
    "products" :transform_products,
    "fixed_costs" : transform_fixed_costs

}