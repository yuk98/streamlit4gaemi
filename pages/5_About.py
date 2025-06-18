import streamlit as st

st.title("💡 이 애플리케이션에 대하여")
st.write("""
    이 애플리케이션은 **Streamlit**과 **Plotly**를 사용하여 CSV 파일로부터
    인터랙티브한 데이터 시각화를 제공하는 데모 앱입니다.
    """)
st.write("""
    **주요 기능:**
    -   CSV 파일에서 데이터를 로드하고 시각화합니다.
    -   다양한 분석 페이지 간의 쉬운 탐색을 지원합니다.
    -   Plotly를 기반으로 하는 풍부한 상호작용 차트를 제공합니다.
    -   Python으로 개발되어 손쉽게 개발 및 관리가 가능합니다.
    -   간단한 익명 게시판 기능을 제공하여 사용자 간 소통이 가능합니다.
    """)
st.write("---")
st.header("기술 스택")
st.markdown("""
* **프론트엔드/백엔드:** Streamlit (Python)
* **차트 라이브러리:** Plotly (Python)
* **데이터 처리:** Pandas (Python)
* **데이터 저장:** CSV (주식 데이터), JSON (게시글 데이터)
""")

st.write("---")
st.write("© 2025 Your Name/Company Name. All rights reserved.")
st.write("문의: example@example.com")