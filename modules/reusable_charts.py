# modules/reusable_charts.py

import pandas as pd

def get_dual_pane_chart_option(dates, series_data, pane1_config, pane2_config, zoom_start_value=None, zoom_end_value=None, backgroundColor='#ffffff'):
    """
    Generates the option dictionary for a 2-pane chart.
    - The font size of the Y-axis labels is set to 10px.
    """
    final_series = [
        {
            "name": name, "type": 'line', "smooth": True, "data": [val if pd.notna(val) else None for val in data],
            "connectNulls": True, "showSymbol": False, "lineStyle": {"width": 2},
            "xAxisIndex": 0 if name in pane1_config['series_names'] else 1,
            "yAxisIndex": 0 if name in pane1_config['series_names'] else 1,
        }
        for name, data in series_data.items()
    ]

    # [수정] 자바스크립트 포맷터는 제거합니다.
    tooltip_position_formatter = "function (point, params, dom, rect, size) { return [point[0] + 15, point[1] - 40]; }"

    echarts_option = {
        "backgroundColor": backgroundColor,
        "color": ['#5470C6', '#91CC75', '#EE6666', '#FAC858', '#73C0DE'],
        "title": [
            {"text": pane1_config['title'], "left": '10%', "top": '3%', "textStyle": {"color": '#000000', "fontSize": 15}},
            {"text": pane2_config['title'], "left": '10%', "top": '54%', "textStyle": {"color": '#000000', "fontSize": 15}}
        ],
        "legend": [
            {"data": pane1_config['series_names'], "top": '7%', "right": '15%', "textStyle": {"color": '#000000'}},
            {"data": pane2_config['series_names'], "top": '58%', "right": '15%', "textStyle": {"color": '#000000'}}
        ],
        "tooltip": {
            "trigger": 'axis', "backgroundColor": 'rgba(255, 255, 255, 0.9)', "borderColor": '#ccc', 
            "borderWidth": 1, "textStyle": {"color": '#000000'},
            "position": tooltip_position_formatter
        },
        "axisPointer": {"link": [{"xAxisIndex": 'all'}], "label": {"backgroundColor": '#777'}},
        "graphic": {
            "type": 'line', "left": '4%', "right": '10%', "top": '56%',
            "shape": {"x1": 0, "y1": 0, "x2": 1, "y2": 0},
            "style": {"stroke": '#dcdcdc', "lineWidth": 1}
        },
        "grid": [
            {"left": '10%', "right": '15%', "top": '15%', "height": '35%', "containLabel": True},
            {"left": '10%', "right": '15%', "top": '65%', "height": '25%', "containLabel": True}
        ],
        "xAxis": [
            {"type": 'category', "data": dates, "scale": True, "boundaryGap": False,
             "splitLine": {"show": True,"lineStyle": {"color": '#cccccc'}}, 
             "axisLine": {"lineStyle": {"color": '#aaa'}}, 
             "axisLabel": {"show": False}},
            {"type": 'category', "gridIndex": 1, "data": dates, "scale": True, "boundaryGap": False,
             "splitLine": {"show": True,"lineStyle": {"color": '#cccccc'}}, 
             "axisLine": {"lineStyle": {"color": '#aaa'}}, 
             "axisLabel": {"color": '#000000', "margin": 20, "fontSize": 12}
            }
        ],

        # [수정] y축 눈금의 글자 크기(fontSize)를 10으로 지정
        "yAxis": [
            {
                "scale": True, 
                "position": 'right',
                "splitLine": {"lineStyle": {"color": '#cccccc'}}, 
                "axisLine": {"lineStyle": {"color": "#f0f2f6"}}, 
                "axisLabel": {"margin": -45, "inside": True, "position": "top", "color": '#000000', "fontSize": 12} # 글자 크기 지정
            },
            {
                "scale": True, 
                "gridIndex": 1, 
                "position": 'right',
                "splitLine": {"lineStyle": {"color": '#cccccc'}}, 
                "axisLine": {"lineStyle": {"color": "#cccccc"}}, 
                "axisLabel": {"margin": -45, "inside": True, "position": "top", "color": '#000000', "fontSize": 12} # 글자 크기 지정
            }
        ],
        "dataZoom": [
            {
                "type": 'slider', 
                "xAxisIndex": [0, 1], 
                "bottom": 15, 
                "startValue": zoom_start_value,
                "endValue": zoom_end_value
            },
            {
                "type": 'inside', 
                "xAxisIndex": [0, 1],
                "startValue": zoom_start_value,
                "endValue": zoom_end_value
            }
        ],
        "series": final_series
    }
    return echarts_option



# import pandas as pd

# def get_multi_pane_chart_option(dates, series_data, *pane_configs, zoom_start_value=None, zoom_end_value=None, backgroundColor='#ffffff'):
#     """
#     Generates a generalized ECharts option for a multi-pane chart (2, 3, 4, etc.).
#     The number of panes is determined by the number of pane_config arguments.

#     Args:
#         dates (list): List of dates for the x-axis.
#         series_data (dict): Dictionary of all series data, e.g., {'series_name': [data_points, ...]}.
#         *pane_configs (dict): A variable number of pane configuration dictionaries.
#                               Each dict must contain 'title' (str) and 'series_names' (list).
#         zoom_start_value (any, optional): The starting value for the data zoom. Defaults to None.
#         zoom_end_value (any, optional): The ending value for the data zoom. Defaults to None.
#         backgroundColor (str, optional): The chart's background color. Defaults to '#ffffff'.

#     Returns:
#         dict: The ECharts option dictionary.
#     """
#     num_panes = len(pane_configs)
#     if num_panes < 2:
#         raise ValueError("This function is for multi-pane charts. Please provide at least 2 pane configurations.")

#     # --- 1. 시리즈 이름과 패널 인덱스 매핑 ---
#     series_to_pane_map = {}
#     for i, config in enumerate(pane_configs):
#         for series_name in config.get('series_names', []):
#             series_to_pane_map[series_name] = i

#     # --- 2. 시리즈 데이터 생성 ---
#     final_series = []
#     for name, data in series_data.items():
#         pane_index = series_to_pane_map.get(name)
#         if pane_index is None:
#             # 설정에 포함되지 않은 시리즈는 건너뛰거나 에러 발생
#             print(f"Warning: Series '{name}' is not assigned to any pane and will be ignored.")
#             continue
        
#         final_series.append({
#             "name": name, "type": 'line', "smooth": True,
#             "data": [val if pd.notna(val) else None for val in data],
#             "connectNulls": True, "showSymbol": False, "lineStyle": {"width": 2},
#             "xAxisIndex": pane_index, "yAxisIndex": pane_index,
#         })

#     # --- 3. 동적 레이아웃 계산 ---
#     # 전체 차트 영역에서 상단 여백(title), 하단 여백(zoom), 패널 간 간격을 뺀 나머지 공간을 n등분
#     CHART_AREA_TOP_PERCENT = 10
#     CHART_AREA_BOTTOM_PERCENT = 12 # dataZoom과 x-axis 라벨 공간
#     PANE_SPACING_PERCENT = 6 # 각 패널 사이의 간격

#     total_grid_space = 100 - CHART_AREA_TOP_PERCENT - CHART_AREA_BOTTOM_PERCENT
#     total_spacing = (num_panes - 1) * PANE_SPACING_PERCENT
#     grid_height = (total_grid_space - total_spacing) / num_panes

#     # --- 4. ECharts 컴포넌트 동적 생성 ---
#     titles, legends, grids, x_axes, y_axes, graphics = [], [], [], [], [], []
#     current_top = CHART_AREA_TOP_PERCENT

#     for i, config in enumerate(pane_configs):
#         # Grid
#         grids.append({
#             "left": '10%', "right": '15%', "containLabel": True,
#             "top": f'{current_top}%',
#             "height": f'{grid_height}%',
#         })
        
#         # Title & Legend
#         titles.append({"text": config['title'], "left": '10%', "top": f'{current_top - 6}%', "textStyle": {"color": '#000000', "fontSize": 15}})
#         legends.append({"data": config['series_names'], "top": f'{current_top - 3}%', "right": '15%', "textStyle": {"color": '#000000'}})
        
#         # X-Axis
#         is_last_pane = (i == num_panes - 1)
#         x_axes.append({
#             "type": 'category', "data": dates, "scale": True, "boundaryGap": False,
#             "gridIndex": i,
#             "splitLine": {"show": True, "lineStyle": {"color": '#cccccc'}},
#             "axisLine": {"lineStyle": {"color": '#aaa'}},
#             "axisLabel": {"show": is_last_pane, "color": '#000000', "margin": 15, "fontSize": 12}
#         })
        
#         # Y-Axis
#         y_axes.append({
#             "scale": True, "position": 'right', "gridIndex": i,
#             "splitLine": {"lineStyle": {"color": '#cccccc'}},
#             "axisLine": {"lineStyle": {"color": "#f0f2f6"}},
#             "axisLabel": {"margin": -45, "inside": True, "position": "top", "color": '#000000', "fontSize": 10}
#         })
        
#         # Separator Line (마지막 패널 제외)
#         if not is_last_pane:
#             separator_top = current_top + grid_height + (PANE_SPACING_PERCENT / 2)
#             graphics.append({
#                 "type": 'line', "left": '4%', "right": '10%', "top": f'{separator_top}%',
#                 "shape": {"x1": 0, "y1": 0, "x2": 1, "y2": 0},
#                 "style": {"stroke": '#dcdcdc', "lineWidth": 1}
#             })
            
#         # 다음 grid의 top 위치 업데이트
#         current_top += grid_height + PANE_SPACING_PERCENT

#     # --- 5. 최종 옵션 조합 ---
#     echarts_option = {
#         "backgroundColor": backgroundColor,
#         "color": ['#5470C6', '#91CC75', '#EE6666', '#FAC858', '#73C0DE', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'],
#         "title": titles,
#         "legend": legends,
#         "tooltip": {
#             "trigger": 'axis', "backgroundColor": 'rgba(255, 255, 255, 0.9)', "borderColor": '#ccc', 
#             "borderWidth": 1, "textStyle": {"color": '#000000'},
#         },
#         "axisPointer": {"link": [{"xAxisIndex": list(range(num_panes))}], "label": {"backgroundColor": '#777'}},
#         "graphic": graphics,
#         "grid": grids,
#         "xAxis": x_axes,
#         "yAxis": y_axes,
#         "dataZoom": [
#             {"type": 'slider', "xAxisIndex": list(range(num_panes)), "bottom": 10, "height": 20, "startValue": zoom_start_value, "endValue": zoom_end_value},
#             {"type": 'inside', "xAxisIndex": list(range(num_panes)), "startValue": zoom_start_value, "endValue": zoom_end_value}
#         ],
#         "series": final_series
#     }
#     return echarts_option


import pandas as pd
import numpy as np

# 'reusable_charts.py' 파일에서 함수를 import 했다고 가정
# from modules.reusable_charts import get_multi_pane_chart_option

# 이 함수는 수정할 필요 없이 그대로 사용합니다.
def get_multi_pane_chart_option(dates, series_data, *pane_configs, zoom_start_value=None, zoom_end_value=None, backgroundColor='#ffffff'):
    """
    Generates a generalized ECharts option for a multi-pane chart (2, 3, 4, etc.).
    The number of panes is determined by the number of pane_config arguments.
    """
    num_panes = len(pane_configs)
    if num_panes < 2:
        raise ValueError("This function is for multi-pane charts. Please provide at least 2 pane configurations.")

    series_to_pane_map = {}
    for i, config in enumerate(pane_configs):
        for series_name in config.get('series_names', []):
            series_to_pane_map[series_name] = i

    final_series = []
    for name, data in series_data.items():
        pane_index = series_to_pane_map.get(name)
        if pane_index is None:
            # 이 부분은 이제 실행되지 않습니다.
            # print(f"Warning: Series '{name}' is not assigned to any pane and will be ignored.")
            continue
        
        final_series.append({
            "name": name, "type": 'line', "smooth": True,
            "data": [val if pd.notna(val) else None for val in data],
            "connectNulls": True, "showSymbol": False, "lineStyle": {"width": 2},
            "xAxisIndex": pane_index, "yAxisIndex": pane_index,
        })

    CHART_AREA_TOP_PERCENT = 10
    CHART_AREA_BOTTOM_PERCENT = 12
    PANE_SPACING_PERCENT = 6

    total_grid_space = 100 - CHART_AREA_TOP_PERCENT - CHART_AREA_BOTTOM_PERCENT
    total_spacing = (num_panes - 1) * PANE_SPACING_PERCENT
    grid_height = (total_grid_space - total_spacing) / num_panes

    titles, legends, grids, x_axes, y_axes, graphics = [], [], [], [], [], []
    current_top = CHART_AREA_TOP_PERCENT

    for i, config in enumerate(pane_configs):
        grids.append({"left": '10%', "right": '15%', "containLabel": True, "top": f'{current_top}%', "height": f'{grid_height}%'})
        titles.append({"text": config['title'], "left": '10%', "top": f'{current_top - 6}%', "textStyle": {"color": '#000000', "fontSize": 15}})
        legends.append({"data": config['series_names'], "top": f'{current_top - 3}%', "right": '15%', "textStyle": {"color": '#000000'}})
        
        is_last_pane = (i == num_panes - 1)
        x_axes.append({
            "type": 'category', "data": dates, "scale": True, "boundaryGap": False, "gridIndex": i,
            "splitLine": {"show": True, "lineStyle": {"color": '#cccccc'}},
            "axisLine": {"lineStyle": {"color": '#aaa'}},
            "axisLabel": {"show": is_last_pane, "color": '#000000', "margin": 15, "fontSize": 12}
        })
        y_axes.append({
            "scale": True, "position": 'right', "gridIndex": i,
            "splitLine": {"lineStyle": {"color": '#cccccc'}}, "axisLine": {"lineStyle": {"color": "#f0f2f6"}},
            "axisLabel": {"margin": -45, "inside": True, "position": "top", "color": '#000000', "fontSize": 10}
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

