import pandas as pd

def build_dim_date(start_date:str,end_date:str) -> pd.DataFrame:

    dates:pd.DatetimeIndex = pd.date_range('2026-01-01','2026-12-31',freq='D')
    dates_df:pd.DataFrame = pd.DataFrame(data= dates,columns=['date'],index=None)

    dates_df['year']= dates_df['date'].dt.year
    dates_df['month']= dates_df['date'].dt.month
    dates_df['day'] = dates_df['date'].dt.day
    dates_df['day_name'] = dates_df["date"].dt.day_name()
    dates_df['weekday'] = dates_df['date'].dt.weekday
    dates_df['month_abrev'] = dates_df['date'].dt.strftime("%b")
    dates_df['month_name'] = dates_df['date'].dt.month_name()
    dates_df['year_month'] = dates_df['date'].dt.strftime("%Y-%m")
    dates_df['year_month_desc'] = dates_df['date'].dt.strftime("%b-%Y")
    dates_df['quarter'] = dates_df["date"].dt.quarter

    dates_df['is_weekend'] = dates_df["date"].dt.weekday > 4
    dates_df['week_of_year'] = dates_df["date"].dt.isocalendar().week
    return dates_df





def build_dim_products(df_products:pd.DataFrame,date:str|None= None)-> pd.DataFrame:
    products = df_products.copy()


    # 1 - fullfill a column snapshot_date with the information pass before
    if date is not None:
        date= pd.to_datetime(date,dayfirst=True)
        products['snapshot_date'] = date

    else:
        products['snapshot_date'] = pd.NaT

    return products





def build_fact_sales(df_sales:pd.DataFrame) -> pd.DataFrame:
    sales:pd.DataFrame = df_sales.copy()
    return sales


def build_fact_fixed_costs(df_fixed_cost:pd.DataFrame) -> pd.DataFrame:
    costs = df_fixed_cost.copy()
    costs['total_fixed_cost_brl']= costs[['rent_brl','payroll_brl','utilities_brl','other_costs_brl']].sum(axis=1)
    return costs




def build_dim_stores(df_stores:pd.DataFrame) -> pd.DataFrame:
    stores = df_stores.copy()
    return stores




def build_gold_model(dataframes_silver: dict[str, pd.DataFrame],start_date:str,end_date:str)-> dict[str, pd.DataFrame]:
    #Extract each DataFrame from the Silver dictionary
    df_products:pd.DataFrame = dataframes_silver['products']
    df_sales:pd.DataFrame = dataframes_silver['sales']
    df_stores:pd.DataFrame = dataframes_silver['stores']
    df_fixed_cost:pd.DataFrame= dataframes_silver['fixed_costs']


    #Build each dataframe gold
    df_products= build_dim_products(df_products)
    df_sales= build_fact_sales(df_sales)
    df_stores= build_dim_stores(df_stores)
    df_fixed_costs= build_fact_fixed_costs(df_fixed_cost)
    df_dim_date= build_dim_date(start_date,end_date)

    return {
        "dim_products": df_products,
        "fact_sales": df_sales,
        "dim_stores": df_stores,
        "fact_fixed_costs": df_fixed_costs,
        "dim_date": df_dim_date,
    }













