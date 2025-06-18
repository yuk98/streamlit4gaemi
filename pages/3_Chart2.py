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
# 이 과정은 차트 컴포넌트에 데이터를 전달하기 위해 필요합니다.
try:
    df_stocks = load_data("data/stock_data.csv")
    df_indicators = load_data("data/indicator_data.csv")

    # 각 패널에 사용할 컬럼 정의
    pane1_cols = df_stocks.columns.tolist()
    pane2_cols = df_indicators.columns.tolist()

    # 패널별 데이터프레임 선택
    df1 = df_stocks[pane1_cols]
    df2 = df_indicators[pane2_cols]

    # 두 데이터프레임의 날짜를 통합하여 전체 기간의 인덱스 생성
    combined_index = df1.index.union(df2.index)
    full_date_range = pd.date_range(start=combined_index.min(), end=combined_index.max())
    
    # 전체 기간에 맞춰 데이터프레임 재정렬 (결측치는 NaN으로 채워짐)
    df1_reindexed = df1.reindex(full_date_range)
    df2_reindexed = df2.reindex(full_date_range)

    # --- 차트 컴포넌트 생성 및 표시 ---
    
    # 1. InteractiveStockChart 클래스에 전달할 인자들을 준비합니다.
    chart_dates = full_date_range.strftime('%Y-%m-%d').tolist()
    chart_series_data = {**df1_reindexed.to_dict('list'), **df2_reindexed.to_dict('list')}

    pane1_config = {"title": "주가 (Price)", "series_names": pane1_cols}
    pane2_config = {"title": "거래량 (Volume)", "series_names": pane2_cols}

    # 2. 준비된 인자들로 차트 컴포넌트의 인스턴스를 생성합니다.
    interactive_chart = InteractiveStockChart(
        dates=chart_dates,
        series_data=chart_series_data,
        pane1_config=pane1_config,
        pane2_config=pane2_config
    )
    
    # 3. display() 메소드를 호출하여 화면에 컴포넌트를 그립니다.
    interactive_chart.display()

except FileNotFoundError:
    st.error("오류: `data/stock_data.csv` 와 `data/indicator_data.csv` 파일이 필요합니다.")
    st.info("현재 디렉토리에 'data' 폴더를 만들고 그 안에 CSV 파일들을 넣어주세요.")

