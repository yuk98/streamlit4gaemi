import streamlit as st
import pandas as pd
from modules.reusable_charts import get_dual_pane_chart_option  # 옵션 생성 함수만 임포트
from streamlit_echarts import st_echarts  # 차트 표시 함수는 페이지에서 직접 사용

st.header("주식 분석 대시보드 (차트 & 위젯 혼합 레이아웃)")

@st.cache_data
def load_data(filepath):
    # 날짜 컬럼을 파싱하여 인덱스로 설정하는 것이 중요합니다.
    df = pd.read_csv(filepath, parse_dates=['date']).set_index('date')
    return df

# 1. 데이터 로딩
df_stocks = load_data("data/stock_data.csv")
df_indicators = load_data("data/indicator_data.csv")


st.subheader("종합 시세 차트")

# 패널별로 표시할 컬럼을 선택합니다.
pane1_cols = ['stock_A_close', 'stock_B_close']
pane2_cols = ['stock_A_volume', 'stock_B_volume']

# 데이터프레임에서 필요한 부분만 선택합니다.
df1 = df_stocks[pane1_cols]
df2 = df_indicators

# 통합된 날짜 인덱스를 생성합니다. (NaN 처리를 위해 필수)
combined_index = df1.index.union(df2.index)
full_date_range = pd.date_range(start=combined_index.min(), end=combined_index.max())

df1 = df1.reindex(full_date_range)
df2 = df2.reindex(full_date_range)

# 재사용 함수를 호출하여 차트 옵션 '객체(딕셔너리)'를 생성합니다.
chart_option_object = get_dual_pane_chart_option(
    dates=full_date_range.strftime('%Y-%m-%d').tolist(),
    series_data={**df1.to_dict('list'), **df2.to_dict('list')},
    pane1_config={"title": "주가 (Price)", "series_names": pane1_cols},
    pane2_config={"title": "거래량 (Volume)", "series_names": df_indicators.columns.tolist()}
)

# 생성된 옵션 객체를 사용하여 원하는 위치에 차트를 표시합니다.
st_echarts(options=chart_option_object, height="600px")
