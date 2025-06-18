import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Portfolio Performance Dashboard")
st.write("환영합니다! 이 대시보드에서 전반적인 자산 추이를 확인해 보세요.")
st.markdown("---")

# CSV 파일 로드 함수 (캐싱 적용)
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. 프로젝트 루트에 있는지 확인해주세요.")
        return pd.DataFrame() # 빈 데이터프레임 반환

# 데이터 로드
df = load_data('data.csv')

if not df.empty:
    # 전체 기간 수익률 차트 (라인 차트)
    st.header("전체 포트폴리오 성과")
    fig_overall = px.line(df, x='Date', y=['StockA', 'StockB', 'StockC'],
                          title='기간별 주식 성과',
                          labels={'value': '가격', 'variable': '종목'},
                          hover_data={"Date": "|%Y-%m-%d"})
    fig_overall.update_layout(hovermode="x unified")
    st.plotly_chart(fig_overall, use_container_width=True)

    st.markdown("---")

    # 데이터 요약 테이블
    st.header("데이터 요약")
    st.dataframe(df.describe())

    st.markdown("---")

    # 추가 콘텐츠: 시장 뉴스 섹션 (가상)
    st.header("오늘의 시장 주요 뉴스")
    st.info("""
    **✅ [속보] 코스피, 외국인 매수세에 힘입어 상승 마감!**
    주요 기술주 강세가 시장 분위기를 이끌었습니다.
    """)
    st.info("""
    **✅ [분석] 인플레이션 압력 완화 조짐?**
    최근 발표된 소비자 물가지수가 예상보다 낮게 나오면서 금리 인상 속도 조절 기대감이 커지고 있습니다.
    """)
else:
    st.warning("데이터 로드에 문제가 발생했습니다. 대시보드를 표시할 수 없습니다.")