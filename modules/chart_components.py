import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_echarts import st_echarts
from .multi_pane_charts import get_multi_pane_chart_option


import streamlit as st
import pandas as pd
from datetime import datetime, date

# 실제 환경에서는 get_multi_pane_chart_option를 임포트합니다.
from .multi_pane_charts import get_multi_pane_chart_option

class InteractiveStockChart:
    """
    [최종 버전] 고유한 state_key를 사용하여 각 차트 인스턴스의 상태를
    완전히 독립적으로 관리하며, 모든 상호작용에서 안정적으로 동작합니다.
    """
    PERIOD_MAPPING = {
        "1년": 1, "3년": 3, "5년": 5, "10년": 10, "전체": None
    }

    def __init__(self, *pane_configs, state_key: str, chart_backgroundColor: str = '#ffffff', default_year: int = 10):
        # 각 차트를 구분하기 위한 고유한 state_key를 필수로 받습니다.
        if not state_key or not isinstance(state_key, str):
            raise ValueError("각 차트를 구분하기 위한 고유한 'state_key' (문자열)를 반드시 제공해야 합니다.")
        self.state_key = state_key

        if not pane_configs:
            raise ValueError("하나 이상의 패널 설정이 필요합니다.")
        for config in pane_configs:
            if not all(k in config for k in ['title', 'data']) or not isinstance(config['data'], pd.DataFrame):
                raise ValueError("모든 패널 설정은 'title'과 pandas DataFrame 타입의 'data'를 포함해야 합니다.")

        self.pane_configs = pane_configs
        self.chart_backgroundColor = chart_backgroundColor
        self.default_year = default_year

        # 모든 날짜 관련 변수는 datetime.date 객체로 통일합니다.
        combined_index = pd.Index([])
        for config in pane_configs:
            combined_index = combined_index.union(config['data'].index)
        self.min_date = combined_index.min().date()
        self.max_date = combined_index.max().date()

        # 모든 상호작용 시 실행되어 날짜 상태를 검증하고 동기화합니다.
        self._validate_and_sync_state()

    def _get_state_key(self, base_key: str) -> str:
        """기본 키에 state_key를 접두사로 붙여 고유한 키를 생성합니다."""
        return f"{self.state_key}_{base_key}"

    def _validate_and_sync_state(self):
        """세션 상태와 현재 데이터 범위의 교집합을 계산하고, 없으면 기본값으로 재설정합니다."""
        start_date_key = self._get_state_key("start_date")
        end_date_key = self._get_state_key("end_date")
        counter_key = self._get_state_key("chart_key_counter")

        desired_start = st.session_state.get(start_date_key)
        desired_end = st.session_state.get(end_date_key)

        if desired_start is None or desired_end is None:
            self._reset_to_default_range(force_remount=False)
            return

        intersection_start = max(desired_start, self.min_date)
        intersection_end = min(desired_end, self.max_date)

        if intersection_start <= intersection_end:
            st.session_state[start_date_key] = intersection_start
            st.session_state[end_date_key] = intersection_end
        else:
            self._reset_to_default_range(force_remount=True)

        if counter_key not in st.session_state:
            st.session_state[counter_key] = 0

    def _reset_to_default_range(self, force_remount: bool = True):
        """날짜 범위를 현재 데이터의 기본값으로 안전하게 재설정합니다."""
        end_date = self.max_date
        if self.default_year:
            start_date_ts = pd.Timestamp(end_date) - pd.DateOffset(years=self.default_year)
            start_date_ts = max(pd.Timestamp(self.min_date), start_date_ts)
            st.session_state[self._get_state_key("start_date")] = start_date_ts.date()
        else:
            st.session_state[self._get_state_key("start_date")] = self.min_date

        st.session_state[self._get_state_key("end_date")] = end_date

        if force_remount:
            key = self._get_state_key("chart_key_counter")
            st.session_state[key] = st.session_state.get(key, 0) + 1

    def _handle_period_selection(self):
        """기간 선택 라디오 버튼의 콜백 함수."""
        radio_key = self._get_state_key("period_radio")
        selected_period_text = st.session_state[radio_key]
        years = self.PERIOD_MAPPING.get(selected_period_text)

        end_date = self.max_date
        if years:
            start_date_ts = pd.Timestamp(end_date) - pd.DateOffset(years=years)
            start_date_ts = max(pd.Timestamp(self.min_date), start_date_ts)
            st.session_state[self._get_state_key('start_date')] = start_date_ts.date()
        else:
            st.session_state[self._get_state_key('start_date')] = self.min_date
        st.session_state[self._get_state_key('end_date')] = end_date

        counter_key = self._get_state_key('chart_key_counter')
        st.session_state[counter_key] = st.session_state.get(counter_key, 0) + 1

    def _display_widgets(self):
        """차트 기간 설정을 위한 위젯들을 표시합니다."""
        with st.container(border=True):
            st.write("**차트 기간 설정**")

            st.radio(
                label="**기간 선택**",
                options=list(self.PERIOD_MAPPING.keys()),
                key=self._get_state_key("period_radio"),
                on_change=self._handle_period_selection,
                horizontal=True,
                index=list(self.PERIOD_MAPPING.values()).index(self.default_year),
                label_visibility="collapsed"
            )

            cal_cols = st.columns(2)
            cal_cols[0].date_input("시작일", key=self._get_state_key('start_date'), min_value=self.min_date, max_value=self.max_date)
            cal_cols[1].date_input("종료일", key=self._get_state_key('end_date'), min_value=self.min_date, max_value=self.max_date)

    def display(self):
        """차트와 제어 위젯을 Streamlit에 최종적으로 표시합니다."""
        start_date_key = self._get_state_key('start_date')
        end_date_key = self._get_state_key('end_date')
        counter_key = self._get_state_key('chart_key_counter')

        with st.container(border=True):
            chart_options = get_multi_pane_chart_option(
                *self.pane_configs,
                zoom_start_value=st.session_state[start_date_key].strftime('%Y-%m-%d'),
                zoom_end_value=st.session_state[end_date_key].strftime('%Y-%m-%d'),
                backgroundColor=self.chart_backgroundColor
            )

            counter = st.session_state.get(counter_key, 0)
            dynamic_key = f"interactive_chart_main_{self.state_key}_{counter}"
            st_echarts(options=chart_options, height="650px", key=dynamic_key)
            self._display_widgets()