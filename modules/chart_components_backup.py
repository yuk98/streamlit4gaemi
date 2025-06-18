# modules/chart_components.py

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_echarts import st_echarts
from .reusable_charts import get_dual_pane_chart_option # 실제 환경에서는 주석 해제

class InteractiveStockChart:
    """
    Displays an interactive stock chart with a control panel below it.
    - The control panel is visually grouped in a bordered container.
    """
    def __init__(self, dates: list, series_data: dict, pane1_config: dict, pane2_config: dict, chart_backgroundColor: str = '#ffffff'):
        # ... (기존 __init__ 메소드는 그대로 유지) ...
        self.dates = dates
        self.series_data = series_data
        self.pane1_config = pane1_config
        self.pane2_config = pane2_config
        self.chart_backgroundColor = chart_backgroundColor

        self.min_date = datetime.strptime(self.dates[0], '%Y-%m-%d')
        self.max_date = datetime.strptime(self.dates[-1], '%Y-%m-%d')

        if 'start_date' not in st.session_state:
            st.session_state['start_date'] = self.min_date
        if 'end_date' not in st.session_state:
            st.session_state['end_date'] = self.max_date
        
        if 'chart_key_counter' not in st.session_state:
            st.session_state['chart_key_counter'] = 0

        # --- 추가된 부분: 드롭다운 옵션과 값 매핑 ---
        self.PERIOD_MAPPING = {
            "1년": 1,
            "3년": 3,
            "5년": 5,
            "10년": 10,
            "전체": None
        }

    def _set_date_range(self, years=None):
        # ... (기존 _set_date_range 메소드는 그대로 유지) ...
        end_date = self.max_date
        if years:
            start_date = end_date - pd.DateOffset(years=years)
            st.session_state['start_date'] = max(self.min_date, start_date)
        else:
            st.session_state['start_date'] = self.min_date
        
        st.session_state['end_date'] = end_date
        st.session_state['chart_key_counter'] += 1
    
    # --- 추가된 부분: 드롭다운 변경을 처리하는 콜백 함수 ---
    def _handle_period_selection(self):
        """selectbox의 on_change 콜백으로 호출될 함수"""
        selected_period_text = st.session_state.period_selector
        if selected_period_text in self.PERIOD_MAPPING:
            years = self.PERIOD_MAPPING[selected_period_text]
            self._set_date_range(years)

    # --- 수정된 부분: _display_widgets 메소드를 드롭다운 방식으로 변경 ---
    def _display_widgets(self):
        with st.container(border=True):
            
            # 버튼 대신 st.selectbox(드롭다운)를 사용
            st.write("**한번에 차트 기간 설정**")
            st.selectbox(
                label="**한번에 차트 기간 설정**",
                label_visibility="collapsed", # 레이블을 시각적으로 숨기고 공간도 제거
                options=list(self.PERIOD_MAPPING.keys()),
                key="period_selector",  # session_state에 저장될 키
                on_change=self._handle_period_selection, # 선택이 바뀔 때마다 콜백 함수 호출
                placeholder="기간을 선택하세요...", # 맨 처음에 표시될 안내 문구
                index=None # 맨 처음에 아무것도 선택되지 않은 상태로 시작
            )
            st.write("**달력으로 세밀하게 기간 설정**")
            cal_cols = st.columns(2)
            cal_cols[0].date_input("시작일", key='start_date', min_value=self.min_date, max_value=self.max_date)
            cal_cols[1].date_input("종료일", key='end_date', min_value=self.min_date, max_value=self.max_date)

    def display(self):
        # 전체 컴포넌트를 감싸는 외부 컨테이너
        with st.container(border=True):
            # 1. 차트 표시
            start_date = st.session_state['start_date']
            end_date = st.session_state['end_date']
            
            chart_options = get_dual_pane_chart_option(
                dates=self.dates,
                series_data=self.series_data,
                pane1_config=self.pane1_config,
                pane2_config=self.pane2_config,
                zoom_start_value=start_date.strftime('%Y-%m-%d'),
                zoom_end_value=end_date.strftime('%Y-%m-%d'),
                backgroundColor=self.chart_backgroundColor
            )
            
            dynamic_key = f"interactive_chart_main_{st.session_state.get('chart_key_counter', 0)}"
            st_echarts(options=chart_options, height="600px", key=dynamic_key)

            # 2. 컨트롤 패널 표시
            self._display_widgets()
