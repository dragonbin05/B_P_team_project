import csv
import os
from pathlib import Path
import json
import stock_data
import pandas as pd

def csv_create():
    """
    user_data.json 파일에서 모든 사용자 ID를 읽어와 각 사용자의 주식 정보 CSV 파일을 생성하는 함수.

    기능:
        - user_data.json 파일에서 사용자 ID 목록을 불러옴.
        - 각 ID에 대해 '{id}.csv' 파일이 이미 있으면 건너뜀.
        - 파일이 없으면 ["ticker", "status", "date", "price", "shares"] 헤더를 포함한 새 CSV 파일 생성.
        - 기존 파일이 있으면 아무 작업도 하지 않음(헤더만 추가, 내용은 추가하지 않음).

    주의:
        - user_data.json 파일은 같은 디렉토리에 존재해야 함.
        - 생성되는 CSV 파일은 UTF-8 인코딩 사용.

    예시:
        csv_create()
        # 'user_data.json' 내 모든 id에 대해 각각 'id.csv' 파일 생성됨.
    """
    json_file = Path('user_data.json')

    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys() #id.json 파일의 키값만 모은 리스트

    for i in usernames:
        file_exists = os.path.isfile(f"{i}.csv") # 파일이 없으면 헤더 추가, 있으면 헤더 없이 이어서 저장

        with open(f"{i}.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["ticker", "status", "date", "price", "shares"])  # 헤더 작성
            else:
                pass
            # writer.writerow([id, pw])  # 사용자 정보 저장

def csv_update(stockdata): #인자: 사용자 주식 정보 튜플
    """
    모든 사용자에 대해 주식 정보를 각자의 CSV 파일에 한 줄씩 추가하는 함수.

    Args:
        stockdata (tuple): 한 사용자의 주식 정보를 담은 튜플.
            예시: ('AAPL', '매수', '2024-06-12', 185.6, 10)

    기능:
        - user_data.json 파일에서 모든 사용자 ID 목록을 불러옴.
        - 각 ID에 대해 '{id}.csv' 파일을 열고, 전달받은 주식 정보를 한 줄씩 추가함.
        - 각 CSV 파일은 UTF-8 인코딩 사용.
        - 헤더는 csv_create 함수에서 별도로 관리함.

    예시:
        csv_update(('AAPL', '매수', '2024-06-12', 185.6, 10))
        # 모든 사용자 파일에 해당 주식 정보가 한 줄씩 추가됨.
    """
    json_file = Path('user_data.json')

    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys() #id.json 파일의 키값(id)만 모은 리스트

    for j in usernames:
        with open(f"{j}.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(stockdata)

def sort_all_user_files_by_date(): # 주식 데이터를 날짜순으로 정렬
    """
    모든 사용자별 주식 데이터 CSV 파일을 날짜(date) 기준으로 오름차순 정렬해서 저장하는 함수.

    기능:
        - user_data.json 파일에서 모든 사용자 ID를 불러옴.
        - 각 ID별로 '{id}.csv' 파일을 읽어서 'date' 컬럼 기준으로 정렬함.
        - 정렬된 데이터를 기존 파일에 덮어써서 저장함.
        - 'date' 컬럼은 '%Y-%m-%d' 형식의 날짜로 파싱함.
        - pandas 라이브러리 사용.

    예시:
        sort_all_user_files_by_date()
        # 모든 사용자별 csv 파일이 날짜순으로 정렬됨.
    """
    json_file = Path('user_data.json')
    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys()
    for user in usernames:
        df = pd.read_csv(f"{user}.csv", parse_dates=["date"], date_format="%Y-%m-%d")
        df.sort_values("date", inplace=True)
        df.to_csv(f"{user}.csv", index=False)

def portfoliocsv_create(id):
    """
    특정 사용자의 포트폴리오 정보 저장용 CSV 파일('port_{id}.csv')을 생성하거나, 이미 있으면 아무 작업도 하지 않는 함수.

    Args:
        id (str): 사용자 ID. 이 ID로 파일명이 결정됨.

    기능:
        - 'port_{id}.csv' 파일이 존재하지 않으면 ["ticker", "ratio"] 헤더가 포함된 새 CSV 파일을 생성.
        - 이미 파일이 있으면 추가 작업 없이 그냥 넘어감(내용은 추가하지 않음).
        - 파일은 항상 UTF-8 인코딩으로 저장.

    예시:
        portfoliocsv_create('user1')
        # 'port_user1.csv' 파일이 없으면 헤더와 함께 생성되고, 있으면 아무 변화 없음.
    """
    # json_file = Path(f'port_{id}.csv')

    # with json_file.open('rt') as fp:
    #     usernames = json.load(fp).keys() #id.json 파일의 키값만 모은 리스트

    file_exists = os.path.isfile(f"port_{id}.csv")

    # 파일이 없으면 헤더 추가, 있으면 헤더 없이 이어서 저장
    with open(f"port_{id}.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["ticker", "ratio"])  # 헤더 작성
        else:
            pass
            # writer.writerow([id, pw])  # 사용자 정보 저장

def portfoliocsv_update(id, portfolio):
    """
    주어진 사용자의 포트폴리오 파일에 종목과 비율 정보를 한 줄 추가한다.

    Args:
        id (str): 사용자 ID. 이 값에 따라 'port_{id}.csv' 파일을 찾거나 생성함.
        portfolio (tuple): ('ticker', 'ratio') 형태의 튜플.  
            예시: ('AAPL', 30)

    기능:
        - 'port_{id}.csv' 파일이 있으면 이어서 내용을 추가하고, 없으면 새로 만듦(헤더는 portfoliocsv_create 함수에서 생성).
        - 포트폴리오(종목, 비율) 정보를 CSV 파일에 한 줄씩 추가함.
        - 파일은 항상 UTF-8 인코딩으로 저장.
    """
    with open(f"port_{id}.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(portfolio)


def portfolio(id):
    """
    사용자의 주식 포트폴리오를 인터랙티브하게 입력받아서 파일로 저장하는 함수.

    Args:
        id (str): 사용자 ID. 입력받은 정보는 'port_{id}.csv' 파일에 저장됨.

    기능:
        - 사용자가 직접 주식 티커와 비율을 반복적으로 입력하게 함.
        - 'exit' 또는 '종료' 입력 시 입력 종료.
        - ticker가 올바르지 않으면 재입력 요청.
        - 비율(ratio)이 0~100 사이의 숫자가 아니면 재입력 요청.
        - 각 입력값이 유효하면 ('티커', '비율') 형태로 CSV 파일에 한 줄씩 저장.
        - 입력 도중 언제든 종료 가능.

    사용 예시:
        portfolio('user1')
    """
    print("포트폴리오 설정을 시작합니다. 종료하려면 'exit' 또는 '종료'를 입력해주세요.")

    while True:
        ticker = stock_data.input_stock()

        if ticker == '종료' or ticker.lower() == 'exit':
            print("포트폴리오 입력을 종료합니다.")
            break

        ticker_res = stock_data.resolve_to_ticker(ticker)
        if ticker_res[0] == None:
            a = input("티커가 잘못되었습니다. 종료하시겠습니까? [Y/N]")

            if a == 'Y':
                break

            print("다시 입력해주세요")
            continue
            # if ticker == 'exit' or ticker == 'EXIT' or ticker == '종료':
            #     print("포트폴리오 입력을 종료합니다.")
            #     break
        else:
            ratio = input(f"{ticker_res[0].upper()}의 비율을 입력해주세요: ")
            
        if ratio.isdigit() == False:
            print("잘못 입력했습니다. 숫자를 입력해주세요.")
        elif float(ratio) > 100 or float(ratio) < 0:
            print("비율이 잘못되었습니다. 다시 입력해주세요")
        else:
            portfoliocsv_create(id)
            k = (ticker_res[0].upper(), ratio)
            portfoliocsv_update(id, k)
                ### 비율이 100이 넘으면 오류 리턴/ 티커, 비율이 각 형식에 맞도록 확인

        continue
        # portfoliocsv_create(id)
        # portfoliocsv_update(id, [j.strip() for j in ticker.split(',')])
        # a = input("\'티커, 비율\'을 입력해주세요: ")

def check_and_edit_portfolio_ratio(user_id):
    file_path = f"port_{user_id}.csv"

    while True:
        # 파일 불러오기
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print("포트폴리오 파일이 없습니다.")
            return

        # ratio 합계 계산
        try:
            df['ratio'] = df['ratio'].astype(float)
        except Exception:
            print("ratio 컬럼에 숫자가 아닌 값이 있습니다. CSV를 확인하세요.")
            return

        total_ratio = df['ratio'].sum()
        if total_ratio <= 100:
            print("포트폴리오 비율의 총합이 100 이하입니다.")
            break

        print(f"\n⚠️ [경고] 포트폴리오 비율의 총합이 {total_ratio:.1f}로 100을 초과했습니다.")
        print(f"수정이 필요합니다. 현재 데이터:")
        print(df.reset_index())

        # 수정할 항목 선택
        idx = input("\n수정할 행의 index 번호를 입력하세요 (취소하려면 Enter): ")
        if idx == "":
            print("수정 작업을 취소했습니다.")
            break
        if not idx.isdigit() or int(idx) not in df.index:
            print("유효한 인덱스 번호를 입력하세요.")
            continue
        idx = int(idx)

        # 어떤 값 수정할지
        print(f"\n수정할 내용: {df.loc[idx]}")
        col = input("수정할 컬럼명을 입력하세요 (예: ratio, ticker): ")
        if col not in df.columns:
            print("존재하지 않는 컬럼입니다.")
            continue
        new_value = input(f"{col}의 새 값을 입력하세요: ")
        # 타입 변환 (ratio는 float, ticker는 str)
        if col == "ratio":
            try:
                new_value = float(new_value)
            except ValueError:
                print("숫자만 입력 가능합니다.")
                continue
        df.at[idx, col] = new_value

        # 수정 후 저장
        df.to_csv(file_path, index=False)
        print(f"{idx}번 행의 {col}이(가) 성공적으로 수정되었습니다. 파일이 업데이트 되었습니다.")

        # 합이 100 이하가 될 때까지 반복
        # 바로 break하지 않으면 연속으로 여러 항목을 수정할 수 있음

def remove_zero_ratio_rows(user_id):
    """
    port_{user_id}.csv 파일에서 ratio가 0인 행을 모두 삭제하고 파일을 업데이트하는 함수.
    """
    file_path = f"port_{user_id}.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("포트폴리오 파일이 없습니다.")
        return

    # ratio가 0인 행만 필터링해서 삭제
    df['ratio'] = df['ratio'].astype(float)
    before = len(df)
    df = df[df['ratio'] != 0]
    after = len(df)

    df.to_csv(file_path, index=False)

    print(f"ratio가 0인 {before - after}개 행을 삭제했습니다.")