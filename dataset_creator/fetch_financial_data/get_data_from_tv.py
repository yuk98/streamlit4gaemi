import pandas as pd
import os
def get_close_prices(asset_dict: dict, n_bars: int = 50000, interval='monthly') -> pd.DataFrame:

    from tvDatafeed import TvDatafeed, Interval
    import warnings
    warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
    
    interval_dict = {
                    "monthly" : Interval.in_monthly,
                    "weekly" :  Interval.in_weekly,
                    "daily" : Interval.in_daily
                    }
        
    tv = TvDatafeed(username = "yuk980305", password = "ttkk0305!!")
    # tv = TvDatafeed()
    
    all_price_series = []

    for ticker, exchange in asset_dict.items():
        print(f"Fetching monthly data for '{ticker}' from '{exchange}'...")
        try:
            asset_df = tv.get_hist(
                symbol=ticker,
                exchange=exchange,
                interval=interval_dict[interval],
                n_bars=n_bars
            )

            if asset_df is not None and not asset_df.empty:
                close_series = asset_df['close'].rename(ticker)
                close_series = close_series.resample("ME").last()
                all_price_series.append(close_series)
                print(f"-> Success: Fetched {len(asset_df)} close prices for '{ticker}'.")
            else:
                print(f"-> Warning: No data returned for '{ticker}'.")
        except Exception as e:
            print(f"-> Error fetching data for '{ticker}': {e}")

    if not all_price_series:
        print("Could not fetch data for any assets. Returning an empty DataFrame.")
        return pd.DataFrame()

    final_df = pd.concat(all_price_series, axis=1)
    final_df.sort_index(inplace=True)
    

    # 마지막 인덱스의 월이 현재 월과 같으면 오늘 날짜로 변경
    if not final_df.empty:
        last_idx = final_df.index[-1]
        today = pd.Timestamp.today()
        if last_idx.month == today.month and last_idx.year == today.year:
            # 인덱스의 마지막 값을 오늘 날짜로 변경
            new_index = final_df.index[:-1].tolist() + [today.normalize()]
            final_df.index = pd.DatetimeIndex(new_index)
    
    final_df.index.name = 'Date'
    return final_df

def save_close_prices(asset_dict: dict, interval:str, data_dir : str, file_name : str):
    current_dir = os.path.dirname(__file__)
    project_dir = os.path.join(current_dir, "../..")
    data_dir = os.path.join(project_dir, data_dir)
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, file_name)
    closes_df = get_close_prices(asset_dict=asset_dict, interval=interval)
    closes_df.to_csv(file_path)

if __name__ == "__main__":
    save_close_prices(asset_dict={"KOSPI200":"KRX", "KOSPI":"KRX","KOSDAQ150":"KRX"}, 
                       interval="monthly", data_dir="data/financial_data/krx_idx", file_name="krx_idx")