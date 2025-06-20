import pandas as pd
import numpy as np

def get_multi_pane_chart_option(*pane_configs, zoom_start_value=None, zoom_end_value=None, backgroundColor='#ffffff'):
    """
    [개선된 버전] 여러 개의 DataFrame을 받아 자동으로 축을 정렬하고 다중 패널 차트를 생성합니다.
    [수정] 모든 패널의 인덱스를 통합(union)하여 공통 x축을 생성하고,
           x축을 'time' 타입으로 사용하여 데이터가 없는 지점은 NaN으로 처리합니다.
    """
    num_panes = len(pane_configs)
    if num_panes == 0:
        raise ValueError("차트를 생성하려면 하나 이상의 패널 설정이 필요합니다.")
    for config in pane_configs:
        if not all(k in config for k in ['title', 'data']):
            raise ValueError("모든 패널 설정에는 'title'과 'data' 키가 포함되어야 합니다.")
        if not isinstance(config['data'], pd.DataFrame):
            raise TypeError("패널 데이터는 반드시 pandas DataFrame이어야 합니다.")

    # --- [수정 시작] ---
    # 1. 모든 패널의 인덱스를 통합하여 하나의 공통된 x축 인덱스를 생성합니다.
    combined_index = pd.Index([])
    for config in pane_configs:
        combined_index = combined_index.union(config['data'].index)
    combined_index = combined_index.sort_values() # 시간순으로 정렬
    # --- [수정 끝] ---

    final_series = []
    titles, legends, grids, x_axes, y_axes, graphics = [], [], [], [], [], []

    CHART_AREA_TOP_PERCENT = 15
    CHART_AREA_BOTTOM_PERCENT = 12
    PANE_SPACING_PERCENT = 12
    LEFT_MARGIN_PERCENT = '8%'
    RIGHT_MARGIN_PERCENT = '15%'

    total_grid_space = 100 - CHART_AREA_TOP_PERCENT - CHART_AREA_BOTTOM_PERCENT
    total_spacing = (num_panes - 1) * PANE_SPACING_PERCENT
    grid_height = (total_grid_space - total_spacing) / num_panes if num_panes > 0 else 0
    
    current_top = CHART_AREA_TOP_PERCENT

    for i, config in enumerate(pane_configs):
        pane_df = config['data']
        pane_title = config['title']
        series_names = pane_df.columns.tolist()
        # print(series_names)

        # --- [수정 시작] ---
        # 2. 현재 패널의 데이터를 공통 인덱스에 맞춰 재정렬(reindex)합니다.
        #    이렇게 하면 공통 인덱스에만 있고 현재 패널 데이터에는 없는 날짜에 NaN이 채워집니다.
        df_reindexed = pane_df.reindex(combined_index)

        # 3. 재정렬된 데이터를 기반으로 시리즈 데이터를 [날짜, 값] 쌍으로 만듭니다.
        for name in series_names:
            series_data = [
                [idx.strftime('%Y-%m-%d'), val if pd.notna(val) else None]
                for idx, val in df_reindexed[name].items()
            ]
            final_series.append({
                "name": name, "type": 'line', "smooth": False, "data": series_data,
                "connectNulls": True, "showSymbol": False, "lineStyle": {"width": 2},
                "xAxisIndex": i, "yAxisIndex": i,
            })
        # --- [수정 끝] ---

        grids.append({"left": LEFT_MARGIN_PERCENT, "right": RIGHT_MARGIN_PERCENT, "containLabel": True, "top": f'{current_top}%', "height": f'{grid_height}%'})
        titles.append({"text": pane_title, "left": LEFT_MARGIN_PERCENT, "top": f'{current_top - 8}%', "textStyle": {"color": '#000000', "fontSize": 15}})
        legends.append({"data": series_names, "top": f'{current_top - 4}%', "right": RIGHT_MARGIN_PERCENT, "textStyle": {"color": '#000000'}})

        is_last_pane = (i == num_panes - 1)
            
        x_axes.append({
            "type": 'time', # x축은 'time' 타입 유지
            "gridIndex": i,
            "splitLine": {"show": True, "lineStyle": {"color": '#cccccc'}},
            "axisLine": {"lineStyle": {"color": '#aaa'}},
            "axisLabel": {
                "show": True,
                "color": '#000000',
                "margin": 15,
                "fontSize": 12,
            }
        })
        y_axes.append({
            "scale": True, "position": 'right', "gridIndex": i,
            "splitLine": {"lineStyle": {"color": '#cccccc'}}, "axisLine": {"lineStyle": {"color": "#f0f2f6"}},
            "axisLabel": {"margin": -5, "inside": True, "position": "top", "color": '#000000', "fontSize": 10, "align": "left"}
        })
        
        if not is_last_pane:
            separator_top = current_top + grid_height + (PANE_SPACING_PERCENT / 2)
            graphics.append({
                "type": 'line', "left": '4%', "right": '10%', "top": f'{separator_top}%',
                "shape": {"x1": 0, "y1": 0, "x2": 1, "y2": 0}, "style": {"stroke": '#dcdcdc', "lineWidth": 1}
            })
        current_top += grid_height + PANE_SPACING_PERCENT
    
    echarts_option = {
        "backgroundColor": backgroundColor,
        "color": ['#5470C6', '#91CC75', '#EE6666', '#FAC858', '#73C0DE', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'],
        "title": titles, "legend": legends,
        "tooltip": {"trigger": 'axis', "backgroundColor": 'rgba(255, 255, 255, 0.9)', "borderColor": '#ccc', "borderWidth": 1, "textStyle": {"color": '#000000'}},
        "axisPointer": {"link": [{"xAxisIndex": list(range(num_panes))}], "label": {"backgroundColor": '#777'}},
        "graphic": graphics, "grid": grids, "xAxis": x_axes, "yAxis": y_axes,
        "dataZoom": [
            {"type": 'slider', "xAxisIndex":list(range(num_panes)), "bottom": 20, "height": 30, "startValue": zoom_start_value, "endValue": zoom_end_value},
            # {"type": 'inside', "xAxisIndex": list(range(num_panes)), "startValue": zoom_start_value, "endValue": zoom_end_value}
        ],
        "series": final_series
    }
    return echarts_option