import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
from tqdm import tqdm
import datetime

def save_ttm_yoy_ttm_yoy_df(trade_df, filename):
    # 1. Date 컬럼을 datetime으로 변환하고 인덱스로 설정 (필요시)
    # if not pd.api.types.is_datetime64_any_dtype(trade_df['Date']):
    #     trade_df['Date'] = pd.to_datetime(trade_df['Date'])
    # trade_df = trade_df.set_index('Date')

    # 2. TTM(12개월 rolling sum) 계산
    ttm_df = (
        trade_df
        .groupby('country_name')[['export_amount', 'import_amount', 'trade_balance']]
        .rolling(window=12, min_periods=12).sum()
        .reset_index()
    )
    ttm_df.rename(columns={
        'export_amount': 'ttm_export_amount',
        'import_amount': 'ttm_import_amount',
        'trade_balance': 'ttm_trade_balance'
    }, inplace=True)
    ttm_df = ttm_df.dropna()

    # 3. YoY(%) 계산 (원본값 기준)
    yoy_df = ttm_df[['country_name', 'Date']].copy()
    for col in ['export_amount', 'import_amount', 'trade_balance']:
        # 원본값 가져오기
        yoy_df[f'yoy_{col}'] = (
            trade_df.reset_index().set_index(['country_name', 'Date'])[col].reindex(
                ttm_df.set_index(['country_name', 'Date']).index
            ).values
        )
        # YoY 계산
        yoy_df[f'yoy_{col}'] = (
            yoy_df.groupby('country_name')[f'yoy_{col}']
            .pct_change(periods=12) * 100
        )
    yoy_df = yoy_df.dropna()

    # 4. TTM의 YoY(%) 계산
    ttm_yoy_df = ttm_df[['country_name', 'Date']].copy()
    for col in ['ttm_export_amount', 'ttm_import_amount', 'ttm_trade_balance']:
        ttm_yoy_df[f'ttm_yoy_{col[4:]}'] = (
            ttm_df.groupby('country_name')[col]
            .pct_change(periods=12) * 100
        )
    ttm_yoy_df = ttm_yoy_df.dropna()

    # 5. 파일명 앞에 접두사 붙이기
    base_dir = os.path.dirname(filename)
    base_name = os.path.basename(filename)
    ttm_path = os.path.join(base_dir, 'ttm_' + base_name)
    yoy_path = os.path.join(base_dir, 'yoy_' + base_name)
    ttm_yoy_path = os.path.join(base_dir, 'ttm_yoy_' + base_name)

    # 6. 저장
    ttm_df.round(1).to_csv(ttm_path, index=False, encoding='utf-8-sig')
    yoy_df.round(1).to_csv(yoy_path, index=False, encoding='utf-8-sig')
    ttm_yoy_df.round(1).to_csv(ttm_yoy_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료:\n{ttm_path}\n{yoy_path}\n{ttm_yoy_path}")

def get_mo_trade_data(year:str):
    api_url = "http://apis.data.go.kr/1220000/nationtrade/getNationtradeList"
    params = {
        'serviceKey': 'MkJl3QdHRyYrINDvMu2FCXGzfajpc6rbSwHPY2VQIWFIU/SvTnul2mE0prGloa3VW+wIJXE7A9R+qC84pt9IAw==',
        'strtYymm': year+'01',
        'endYymm': year+'12',
        'cntyCd': ''
    }

    response = requests.get(api_url, params=params)
    # 예시 XML 문자열 (실제 API 응답을 변수에 넣어 사용)
    xml_data =  response.text
    # XML 파싱
    root = ET.fromstring(xml_data)

    # <item> 태그 리스트 가져오기
    items = root.find('body').find('items').findall('item')

    # 각 item의 데이터를 딕셔너리로 추출
    data_list = []
    for item in items:
        data = {
            'year': item.findtext('year'),
            'country_code': item.findtext('statCd'),
            'country_name': item.findtext('statCdCntnKor1'),
            'export_count': int(item.findtext('expCnt')),
            'export_amount': int(item.findtext('expDlr')),
            'import_count': int(item.findtext('impCnt')),
            'import_amount': int(item.findtext('impDlr')),
            'trade_balance': int(item.findtext('balPayments'))
        }
        data_list.append(data)

    # DataFrame 생성
    df = pd.DataFrame(data_list)
    # 결과 출력
    return df

def save_kr_trade_data(start_year=None, end_year=None, target_dir='../data'):

    current_dir = os.path.dirname(__file__)
    target_dir = os.path.join(current_dir, target_dir)
    os.makedirs(target_dir, exist_ok=True)
    save_file_path = os.path.join(target_dir, 'kr_trade_data_by_country.csv')
    save_file_path2 = os.path.join(target_dir, 'kr_trade_data_total.csv')
    save_file_path = os.path.abspath(save_file_path)
    print(f"Saving trade data by country to: {save_file_path}")
    print(f"Saving trade data by all countries to: {save_file_path2}")


    one_yr_df_list = []
    if end_year is None:
        end_year = pd.Timestamp.now().year 
    if start_year is None:
        start_year = 1991

    # for year in range(start_year, end_year):
    for year in tqdm(range(start_year, end_year+1), desc="연도별 데이터 수집"):
        mo_df = get_mo_trade_data(str(year))
        mo_df = mo_df[['year', 'export_amount', 'import_amount', 'trade_balance', 'country_name']].copy()
        mo_df = mo_df.rename(columns={'year': 'Date'})
        one_yr_df_list.append(mo_df)


    long_hist_df = pd.concat(one_yr_df_list, ignore_index=True)

    # 'year' 컬럼으로 그룹화하고 각 그룹의 합계를 계산
    total_df = long_hist_df.groupby('Date').agg({
        'export_amount': 'sum',
        'import_amount': 'sum',
        'trade_balance': 'sum'
    }).reset_index()

    total_df['country_name'] = '총계'

    final_df = pd.concat([long_hist_df, total_df], ignore_index=True)
    final_df = final_df.set_index('Date')
    final_df.index = pd.to_datetime(final_df.index, format='%Y.%m')
    final_df.index = final_df.index + pd.offsets.MonthEnd(0)  # 각 날짜를 해당 월의 월말

    final_df = final_df.sort_index()
    
    trade_by_country_df = final_df[final_df['country_name'] != '총계'].copy()
    trade_by_country_df.to_csv(save_file_path, encoding='utf-8-sig')

    trade_total_df = final_df[final_df['country_name'] == '총계'].copy()
    trade_total_df.to_csv(save_file_path2, encoding='utf-8-sig')

    save_ttm_yoy_ttm_yoy_df(trade_by_country_df, save_file_path)
    save_ttm_yoy_ttm_yoy_df(trade_total_df, save_file_path2)
    print(f"Data saved to {save_file_path} and {save_file_path2}")



if __name__ == "__main__":
    save_kr_trade_data(start_year=1991, end_year=2025, target_dir='../data/trade_data')
    print("Data saved successfully.")