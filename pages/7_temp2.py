import os
import os.path
import streamlit as st
import pandas as pd
from modules.chart_components import InteractiveStockChart # 우리가 만든 차트 컴포넌트 클래스


# 페이지 레이아웃을 넓게 설정하여 차트가 잘 보이도록 합니다.
st.set_page_config(layout="wide")

st.title("인터랙티브 차트 컴포넌트")
st.write("`InteractiveStockChart` 클래스로 생성된 차트 컴포넌트입니다.")

@st.cache_data
def load_data(filepath):
    """CSV 파일을 로드하고 'date' 컬럼을 인덱스로 설정합니다."""
    df = pd.read_csv(filepath, parse_dates=['Date']).set_index('Date')
    return df

@st.cache_data
def load_trade_data_dict(data_dir='data/trade_data', fname='kr_trade_data_total.csv', country_name_lst : list = ['총계']):
    data_dir = os.path.join(os.path.dirname(__file__),"..", data_dir)
    data_dir = os.path.abspath(data_dir)
    # print(data_dir)

    prefixes = [
        'ttm',
        'yoy',
        'ttm_yoy',
        'monthly_trade_data'
    ]
    data_dict = {}
    for country_name in country_name_lst:
        for prefix in prefixes:
            if prefix == 'monthly_trade_data':
                fpath = os.path.join(data_dir, f"{fname}")

            else:
                fpath = os.path.join(data_dir, f"{prefix}_{fname}")
            
            country_name_prefix = country_name + '_'+ prefix

            if os.path.exists(fpath):
                df = pd.read_csv(fpath, parse_dates=['Date'])
                df.set_index('Date', inplace=True)
                
                df = df[df['country_name'] == country_name].drop(columns=['country_name'])
                
                data_dict[country_name_prefix] = df

            else:
                data_dict[country_name_prefix] = None  # 파일이 없으면 None으로 표시

    return data_dict

# --- 데이터 로딩 및 준비 ---
def scale_df(df, scale_factor=1e9):
    if df is not None:
        # 숫자 컬럼만 선택
        num_cols = df.select_dtypes(include='number').columns
        df[num_cols] = df[num_cols] / scale_factor
        return df
    else:
        return None

try:
    file_path = 'data/financial_data/krx_idx/krx_idx.csv'
    file_path = os.path.join( os.path.dirname(__file__), "..", file_path)
    file_path = os.path.abspath(file_path)
    krx_idx = load_data(file_path)
    # krx_idx.set_index("Date", inplace=True)
    Kospi200_df = krx_idx[["KOSPI200"]].dropna().round(0)
    pane1_config = {"title": "Kospi200", "data": Kospi200_df}


    data_dir = 'data/trade_data'  # 데이터가 저장된 디렉토리
    fname = 'kr_trade_data_total.csv'  # 데이터 파일 이름
    country_name_lst = ['총계']

    trade_data_dict = load_trade_data_dict(data_dir=data_dir, fname=fname, country_name_lst=country_name_lst)
    ttm_kr_trade = scale_df(trade_data_dict['총계_ttm'])# 1billion usd
    yoy_kr_trade = trade_data_dict['총계_yoy']
    ttm_yoy_kr_trade = trade_data_dict['총계_ttm_yoy']
    monthly_kr_trade = scale_df(trade_data_dict['총계_monthly_trade_data'])  # 1billion usd

    new_col_names = {
        'ttm_export_amount': '수출액',
        'ttm_import_amount': '수입액',
        'ttm_trade_balance': '무역수지'
    }
    # print("ttm_kr_trade columns:", ttm_kr_trade.columns)
    ttm_kr_trade = ttm_kr_trade.rename(columns=new_col_names)
    # print("ttm_kr_trade columns:", ttm_kr_trade.columns)

    pane2_config = {"title": "12개월 누적 수출입 ($1B)", "data": ttm_kr_trade[['수출액', '수입액']].round(0)}
    pane3_config = {"title": "12개월 누적 무역수지 ($1B)", "data": ttm_kr_trade[['무역수지']].round(0)}

    # 2. [수정] 준비된 설정들을 인자로 하여 차트 컴포넌트의 인스턴스를 생성합니다.
    interactive_chart = InteractiveStockChart(
        pane1_config,
        pane2_config,
        pane3_config,
        state_key= 'kr_trade_data_chart',  # 고유한 state_key를 지정합니다.    
    )

    interactive_chart.display()

    

except FileNotFoundError:
    st.error("오류: `data/stock_data.csv` 와 `data/indicator_data.csv` 파일이 필요합니다.")
    st.info("현재 디렉토리에 'data' 폴더를 만들고 그 안에 CSV 파일들을 넣어주세요.")