import csv
import os
from pathlib import Path
import json

json_file = Path('user_data.json')

with json_file.open('rt') as fp:
    usernames = json.load(fp).keys()

for i in usernames:
    file_exists = os.path.isfile(f"{i}.csv") # 파일이 없으면 헤더 추가, 있으면 헤더 없이 이어서 저장

    with open(f"{i}.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["ticker", "date"])  # 헤더 작성
        # writer.writerow([id, pw])  # 사용자 정보 저장