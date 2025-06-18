import pandas as pd
import numpy as np

def get_multi_pane_chart_option(*pane_configs, zoom_start_value=None, zoom_end_value=None, backgroundColor='#ffffff'):
    """
    [개선된 버전] 여러 개의 DataFrame을 받아 자동으로 축을 정렬하고 다중 패널 차트를 생성합니다.
    Python에서 직접 x축 날짜 라벨 형식을 'YY-MM-DD'로 변경합니다.
    """
    num_panes = len(pane_configs)
    if num_panes == 0:
        raise ValueError("차트를 생성하려면 하나 이상의 패널 설정이 필요합니다.")
    for config in pane_configs:
        if not all(k in config for k in ['title', 'data']):
            raise ValueError("모든 패널 설정에는 'title'과 'data' 키가 포함되어야 합니다.")
        if not isinstance(config['data'], pd.DataFrame):
            raise TypeError("패널 데이터는 반드시 pandas DataFrame이어야 합니다.")

    combined_index = pd.Index([])
    for config in pane_configs:
        combined_index = combined_index.union(config['data'].index)
    
    full_date_range = pd.date_range(start=combined_index.min(), end=combined_index.max(), freq='D')
    # --- [수정] 여기서 날짜 형식을 'YY-MM-DD'로 직접 지정합니다. ---
    # '%Y' (2023) -> '%y' (23)
    dates_str = full_date_range.strftime('%y-%m-%d').tolist()

    # --- 수정 끝 ---

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

        df_reindexed = pane_df.reindex(full_date_range)

        for name in series_names:
            series_data = [val if pd.notna(val) else None for val in df_reindexed[name]]
            final_series.append({
                "name": name, "type": 'line', "smooth": True, "data": series_data,
                "connectNulls": True, "showSymbol": False, "lineStyle": {"width": 2},
                "xAxisIndex": i, "yAxisIndex": i,
            })

        grids.append({"left": LEFT_MARGIN_PERCENT, "right": RIGHT_MARGIN_PERCENT, "containLabel": True, "top": f'{current_top}%', "height": f'{grid_height}%'})
        titles.append({"text": pane_title, "left": LEFT_MARGIN_PERCENT, "top": f'{current_top - 8}%', "textStyle": {"color": '#000000', "fontSize": 15}})
        legends.append({"data": series_names, "top": f'{current_top - 4}%', "right": RIGHT_MARGIN_PERCENT, "textStyle": {"color": '#000000'}})

        is_last_pane = (i == num_panes - 1)
            
        x_axes.append({
            "type": 'category', "data": dates_str, "scale": True, "boundaryGap": False, "gridIndex": i,
            "splitLine": {"show": True, "lineStyle": {"color": '#cccccc'}},
            "axisLine": {"lineStyle": {"color": '#aaa'}},
            # --- [수정] formatter가 필요 없으므로 axisLabel 설정을 원래대로 되돌립니다. ---
            "axisLabel": {
                "show": is_last_pane,
                "color": '#000000',
                "margin": 15,
                "fontSize": 12
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
            {"type": 'slider', "xAxisIndex": list(range(num_panes)), "bottom": 10, "height": 20, "startValue": zoom_start_value, "endValue": zoom_end_value},
            {"type": 'inside', "xAxisIndex": list(range(num_panes)), "startValue": zoom_start_value, "endValue": zoom_end_value}
        ],
        "series": final_series
    }
    return echarts_option