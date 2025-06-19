import time
import datetime
import pytz

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from fetch_trade_data import get_trade_data_by_country

file_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join( file_dir, "../../")
LAST_UPDATE_FILE = os.path.join(project_dir, "last_update_date.txt")

def read_last_update_date():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
            date_str = f.read().strip()
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                return None
    return None

def write_last_update_date(date_obj):
    with open(LAST_UPDATE_FILE, "w", encoding="utf-8") as f:
        date_str = date_obj.strftime("%Y-%m-%d")
        f.write(date_str)
    return date_str


def update_data_all(update_tasks):
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(seoul_tz)
    print(f"{now} - 데이터 업데이트 시작")
    for func, kwargs in update_tasks:
        print(f"실행: {func.__name__}")
        func(**kwargs)
    write_last_update_date(now.date())
    print(f"{now} - 데이터 업데이트 완료")

def loop_update_data(slee_time=600):
    seoul_tz = pytz.timezone('Asia/Seoul')

    # 업데이트 작업 리스트: (함수, kwargs)
    update_tasks = [
        (get_trade_data_by_country.save_kr_trade_data, {'start_year': 1991, 'end_year': 2025, 'target_dir': os.path.join(project_dir, "data", "trade_data")}),
        # (save_other_data_when_old, {'some_arg': 123}),  # 다른 함수도 쉽게 추가 가능
    ]

    while True:
        now = datetime.datetime.now(seoul_tz)
        now_date = now.date()
        now_hour = now.hour

        last_update_date = read_last_update_date()

        # 오후 6시 이후이고, 오늘 아직 업데이트하지 않았다면 실행

        if last_update_date is None:
            print(f"{now} - 마지막 업데이트 날짜를 찾을 수 없습니다. 오늘 업데이트를 시도합니다.")
            update_data_all(update_tasks)

        elif last_update_date != now_date:
            if now_hour >= 18:
                update_data_all(update_tasks)
            else:
                print(f"{now} - 오후 6시 이후에 업데이트를 실행합니다. 현재 시간: {now_hour}시")

        else:
            print(f"{now} - 오늘은 이미 업데이트를 완료했습니다.")

        # 10분마다 체크 (원하면 더 짧게/길게 조정)
        print(f"last_update_date: {last_update_date}, now_date: {now_date}, next check in {slee_time} seconds.")
        time.sleep(slee_time)  # 10분 = 600초

if __name__ == "__main__":
    try:
        loop_update_data(slee_time=600)  # 10분마다 업데이트 체크
    except KeyboardInterrupt:
        print("업데이트 작업이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")