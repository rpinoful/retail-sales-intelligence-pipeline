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


