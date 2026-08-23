import pandas as pd
from src.model import build_dim_date, build_dim_products
import pandas as pd
from src.extract import read_parquet_files
from src.config import SILVER_PATH





# generating a dataframe for date table creation (DIM_DATE)


# python -m exploration_gold.explore_gold

# making function logic
# dates:pd.DatetimeIndex = pd.date_range('2026-01-01','2026-12-31',freq='D')

# dates_df:pd.DataFrame = pd.DataFrame(data= dates,columns=['date'],index=None)

# dates_df['year']= dates_df['date'].dt.year
# dates_df['month']= dates_df['date'].dt.month
# dates_df['day'] = dates_df['date'].dt.day
# dates_df['day_name'] = dates_df["date"].dt.day_name()
# dates_df['weekday'] = dates_df['date'].dt.weekday
# dates_df['month_abrev'] = dates_df['date'].dt.strftime("%b")
# dates_df['name_month'] = dates_df['date'].dt.month_name()
# dates_df['year_month'] = dates_df['date'].dt.strftime("%Y-%m")
# dates_df['year_month_desc'] = dates_df['date'].dt.strftime("%b-%Y")
# dates_df['quarter'] = dates_df["date"].dt.quarter

# dates_df['is_weekend'] = dates_df["date"].dt.weekday > 4
# dates_df['week_of_year'] = dates_df["date"].dt.isocalendar().week


# print(dates_df.head(25))


# dim_date = build_dim_date('2026-01-01','2026-12-31')
# print(dim_date)



# 1 - Receiving all the silver dictionary dataframe 
silver_dataframes:dict[str, pd.DataFrame] = read_parquet_files(SILVER_PATH)



# taking each dataframe
df_products:pd.DataFrame = silver_dataframes['products'].copy()
df_sales:pd.DataFrame = silver_dataframes['sales'].copy()
df_stores:pd.DataFrame = silver_dataframes['stores'].copy()
df_fixed_cost:pd.DataFrame= silver_dataframes['fixed_costs'].copy()
df_dim_date = build_dim_date('2026-01-01','2026-12-31')


# 2 - Building business logic from df_products
# python -m exploration_gold.explore_gold
# print(df_products.head(5))

# print(df_products.duplicated(subset=['product_id']))






# 3 - Building business logic from df_sales
# python -m exploration_gold.explore_gold


#checking if exists duplicated sales:
# business rule if row is a unique sale


#checking if all the product_id coincide with id products from a dimension products
#print((~df_sales['product_id'].isin(df_products['product_id'])).sum())



#checking if all the store_id coincide with id stores from a dimension stores
#print((~df_sales['store_id'].isin(df_stores['store_id'])).sum())



#checking if all dates coincide with dates from a dimension 
print((~df_sales['sale_date'].isin(df_dim_date['date'])).sum())


