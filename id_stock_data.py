import csv
import os
from pathlib import Path
import json



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
                writer.writerow(["ticker", "date"])  # 헤더 작성
            # writer.writerow([id, pw])  # 사용자 정보 저장

def csv_update(stockdata):
    json_file = Path('user_data.json')

    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys() #id.json 파일의 키값만 모은 리스트
        
    for j in usernames:
        with open(f"{j}.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(stockdata)  # 사용자 정보 저장