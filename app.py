import streamlit as st

# 페이지 설정 (전체 앱에 적용)
st.set_page_config(
    page_title="Portfolio Visualizer Clone",
    page_icon="📈",
    layout="wide"
)

st.sidebar.title("Navigation")
# Streamlit이 자동으로 pages/ 폴더 안의 파일들을 페이지로 인식합니다.
# 파일 이름 앞에 붙은 숫자는 정렬 순서를 결정합니다.