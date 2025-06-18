import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_echarts import st_echarts
from .multi_pane_charts import get_multi_pane_chart_option

class InteractiveStockChart:
    """
    [개선된 버전] 다중 패널 설정을 받아 상호작용 가능한 차트와 제어판을 표시합니다.
    """
    def __init__(self, *pane_configs, chart_backgroundColor: str = '#ffffff'):
        if not pane_configs:
            raise ValueError("하나 이상의 패널 설정이 필요합니다.")
        for config in pane_configs:
            if not all(k in config for k in ['title', 'data']) or not isinstance(config['data'], pd.DataFrame):
                raise ValueError("모든 패널 설정은 'title'과 pandas DataFrame 타입의 'data'를 포함해야 합니다.")
        
        self.pane_configs = pane_configs
        self.chart_backgroundColor = chart_backgroundColor

        combined_index = pd.Index([])
        for config in self.pane_configs:
            combined_index = combined_index.union(config['data'].index)

        self.min_date = combined_index.min().to_pydatetime()
        self.max_date = combined_index.max().to_pydatetime()

        if 'start_date' not in st.session_state:
            st.session_state['start_date'] = self.min_date
        if 'end_date' not in st.session_state:
            st.session_state['end_date'] = self.max_date

        if 'chart_key_counter' not in st.session_state:
            st.session_state['chart_key_counter'] = 0

        self.PERIOD_MAPPING = {
            "1년": 1, "3년": 3, "5년": 5, "10년": 10, "전체": None
        }

    def _set_date_range(self, years=None):
        end_date = self.max_date
        if years:
            start_date = pd.Timestamp(end_date) - pd.DateOffset(years=years)
            st.session_state['start_date'] = max(pd.Timestamp(self.min_date), start_date).to_pydatetime()
        else:
            st.session_state['start_date'] = self.min_date

        st.session_state['end_date'] = end_date
        st.session_state['chart_key_counter'] += 1

    def _handle_period_selection(self):
        selected_period_text = st.session_state.period_radio
        if selected_period_text in self.PERIOD_MAPPING:
            years = self.PERIOD_MAPPING[selected_period_text]
            self._set_date_range(years)

    def _display_widgets(self):
        with st.container(border=True):
            st.write("**차트 기간 설정**")
            st.radio(
                label="**한번에 차트 기간 설정**",
                options=list(self.PERIOD_MAPPING.keys()),
                key="period_radio",
                on_change=self._handle_period_selection,
                horizontal=True,
                index=None,
                label_visibility="collapsed"
            )
            cal_cols = st.columns(2)
            cal_cols[0].date_input("시작일", key='start_date', min_value=self.min_date, max_value=self.max_date)
            cal_cols[1].date_input("종료일", key='end_date', min_value=self.min_date, max_value=self.max_date)

    def display(self):
        with st.container(border=True):
            start_date = st.session_state['start_date']
            end_date = st.session_state['end_date']

            chart_options = get_multi_pane_chart_option(
                *self.pane_configs,
                zoom_start_value=start_date.strftime('%y-%m-%d'), # 형식 통일
                zoom_end_value=end_date.strftime('%y-%m-%d'),     # 형식 통일
                backgroundColor=self.chart_backgroundColor
            )

            dynamic_key = f"interactive_chart_main_{st.session_state.get('chart_key_counter', 0)}"
            st_echarts(options=chart_options, height="600px", key=dynamic_key)

            self._display_widgets()