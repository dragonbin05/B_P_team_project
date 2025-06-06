import csv
import os
from pathlib import Path
import json
import stock_data
import ast
import pandas as pd

def csv_create():
    '''
    userdata.json에서 id를 불러와서 'id.csv' 파일을 생성성
    '''
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
    json_file = Path('user_data.json')

    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys() #id.json 파일의 키값(id)만 모은 리스트

    for j in usernames:
        with open(f"{j}.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(stockdata)

def sort_all_user_files_by_date(): # 주식 데이터를 날짜순으로 정렬
    json_file = Path('user_data.json')
    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys()
    for user in usernames:
        df = pd.read_csv(f"{user}.csv", parse_dates=["date"])
        df.sort_values("date", inplace=True)
        df.to_csv(f"{user}.csv", index=False)

def portfoliocsv_create(id):
    '''
    userdata.json에서 id를 불러와서 'id.csv' 파일을 생성성
    '''
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
    with open(f"port_{id}.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(portfolio)


def portfolio(id):
    print("포트폴리오 설정을 시작합니다. 종료하려면 'exit' 또는 '종료'를 입력해주세요.")

    while True:
        ticker = input("티커를 입력해주세요: ")

        if ticker == 'exit' or ticker == 'EXIT' or ticker == '종료':
            print("포트폴리오 입력을 종료합니다.")
            break

        if stock_data.resolve_to_ticker(ticker)[0] == None:
            print("티커가 잘못되었습니다. 다시 입력해주세요")
            continue
            # if ticker == 'exit' or ticker == 'EXIT' or ticker == '종료':
            #     print("포트폴리오 입력을 종료합니다.")
            #     break
        else:
            ratio = input(f"{ticker}의 비율을 입력해주세요: ")
            portfoliocsv_create(id)
            k = (ticker.upper(), ratio)
            portfoliocsv_update(id, k)

        continue
        # portfoliocsv_create(id)
        # portfoliocsv_update(id, [j.strip() for j in ticker.split(',')])
        # a = input("\'티커, 비율\'을 입력해주세요: ")