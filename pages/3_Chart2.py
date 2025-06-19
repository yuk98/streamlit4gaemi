import streamlit as st
import pandas as pd
import numpy as np
# [수정] 새로운 get_multi_pane_chart_option 함수를 임포트합니다.
from modules.multi_pane_charts import get_multi_pane_chart_option
from streamlit_echarts import st_echarts

# --- 1. 샘플 데이터 생성 (인덱스를 날짜로 설정) ---
date_index = pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='D'))
dates_str_list = date_index.strftime('%Y-%m-%d').tolist()

df1 = pd.DataFrame({'Price': np.random.rand(100) * 50 + 100, 'MA20': (np.random.rand(100) * 50 + 100).cumsum() / np.arange(1, 101)}, index=date_index)
df2 = pd.DataFrame({'RSI': np.random.rand(100) * 40 + 30}, index=date_index)
df3 = pd.DataFrame({'MACD': np.random.randn(100), 'Signal': np.random.randn(100)}, index=date_index)
df4 = pd.DataFrame({'Volume': np.random.randint(1000, 5000, size=100)}, index=date_index)

# --- 2. 각 패널에 대한 설정 정의 (DataFrame 직접 포함) ---
pane1_config = {'title': '주가 정보', 'data': df1}
pane2_config = {'title': 'RSI 지표', 'data': df2}
pane3_config = {'title': 'MACD', 'data': df3}
pane4_config = {'title': '거래량', 'data': df4}

# --- 3. 함수 호출 (훨씬 간결해진 방식) ---
# [수정] 별도의 헬퍼 함수나 데이터 필터링 과정이 필요 없습니다.

# 예시 1: 2개 패널 차트
st.header("2-Pane Chart")
options_2_panes = get_multi_pane_chart_option(
    pane1_config, 
    pane4_config # 그리고 싶은 패널 설정만 전달
)
st_echarts(options=options_2_panes, height="600px")


# 예시 2: 3개 패널 차트
st.header("3-Pane Chart")
options_3_panes = get_multi_pane_chart_option(
    pane1_config, 
    pane2_config, 
    pane4_config
)
st_echarts(options=options_3_panes, height="700px")


# 예시 3: 4개 패널 차트
st.header("4-Pane Chart")
options_4_panes = get_multi_pane_chart_option(
    pane1_config, pane2_config, pane3_config, pane4_config,
    zoom_start_value=dates_str_list[50], # zoom 값은 문자열 리스트에서 선택
    zoom_end_value=dates_str_list[99]
)
st_echarts(options=options_4_panes, height="800px")