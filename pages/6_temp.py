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
    df = pd.read_csv(filepath, parse_dates=['date']).set_index('date')
    return df

# --- 데이터 로딩 및 준비 ---
try:
    df_stocks = load_data("data/stock_data.csv")
    df_indicators = load_data("data/indicator_data.csv")

    # --- [수정] 차트 컴포넌트 생성 및 표시 ---
    # 이전의 복잡한 데이터 전처리(인덱스 통합, 재정렬, 데이터 딕셔너리 생성) 과정이 모두 불필요해졌습니다.

    # 1. [수정] InteractiveStockChart 클래스에 전달할 설정을 간단하게 정의합니다.
    # 각 패널에 대한 'title'과 'data'(DataFrame)만 지정하면 됩니다.
    pane1_config = {"title": "주가 (Price)", "data": df_stocks}
    pane2_config = {"title": "거래량 (Volume)", "data": df_indicators}

    # 2. [수정] 준비된 설정들을 인자로 하여 차트 컴포넌트의 인스턴스를 생성합니다.
    interactive_chart = InteractiveStockChart(
        pane1_config,
        pane2_config
    )
    
    # 3. display() 메소드를 호출하여 화면에 컴포넌트를 그립니다. (이 부분은 동일)
    interactive_chart.display()

except FileNotFoundError:
    st.error("오류: `data/stock_data.csv` 와 `data/indicator_data.csv` 파일이 필요합니다.")
    st.info("현재 디렉토리에 'data' 폴더를 만들고 그 안에 CSV 파일들을 넣어주세요.")