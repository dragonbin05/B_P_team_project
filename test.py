from pathlib import Path
import json

json_file = Path('user_data.json')

if json_file.exists() and json_file.stat().st_size > 0:
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}
    
id = input("ID를 입력하시오: ")
pw = input("Password를 입력하시오: ")
data[id] = pw


with json_file.open('w+t') as fp:
    json.dump(data, fp)