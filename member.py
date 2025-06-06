import re
from pathlib import Path
import json
import member

# 특수문자 존재하면 True 반환!
def contains_special_char(s): 
    return bool(re.search(r'[^a-zA-Z0-9\s]', s)) # 특수문자를 의미하는 정규표현식: 알파벳, 숫자, 공백을 제외한 문자

data = {}

def signup():
    while True:
        json_file = Path('user_data.json')

        if json_file.exists() and json_file.stat().st_size > 0:
            with json_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            with json_file.open('w+t') as fp:
                json.dump(data, fp)

        first = input("로그인하려면 Y, 회원가입하려면 N을 입력하세요: ").lower()

        if first == "y": #로그인
            signin()
            break
        elif first == "n": #회원가입
            id = input("회원가입할 ID를 입력하시오: ")
        else:
            print("잘못 입력했습니다. 다시 입력해주세요")
            continue

        with json_file.open('rt') as fp:
            usernames = json.load(fp).keys() #id:pw json 파일

        if id in usernames:
            print("이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요")
            continue
        else:
            print("Password는 영어 소문자, 숫자, 특수기호를 사용할 수 있으며, 특수기호는 적어도 한 개 이상 사용해야 합니다.")
            pw = input("Password를 입력하시오: ")

            # password에 특수문자가 없을 경우 다시 입력하도록 메시지 출력
            while contains_special_char(pw) == False: 
                pw = input("특수문자를 포함해서 Password를 다시 적어주세요")
                if contains_special_char(pw) == True:
                    break

            data[id] = pw

            with json_file.open('w+t') as fp:
                json.dump(data, fp)

            # # 파일이 없으면 헤더 추가, 있으면 헤더 없이 이어서 저장
            # file_exists = os.path.isfile("user_data.csv")

            # with open("user_data.csv", mode="a", newline="", encoding="utf-8") as file:
            #     writer = csv.writer(file)

            #     if not file_exists:
            #         writer.writerow(["username", "password"])  # 헤더 작성

            #     writer.writerow([id, pw])  # 사용자 정보 저장

            print("회원가입이 완료되었습니다!")
            member.id_signin = id
            break

id_signin = ''

def signin():
    exit_all = False

    json_file = Path('user_data.json')

    with json_file.open('rt') as fp:
        usernames = json.load(fp).keys() #id json 파일

    while True:
        #json 파일이 존재하면 열기, 존재하지 않으면 json 파일 생성
        if json_file.exists() and json_file.stat().st_size > 0:
            with json_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
            with json_file.open('w+t') as fp:
                json.dump(data, fp)

        id_signin = input("로그인할 아이디를 입력해주세요: ")
        if id_signin in usernames:
            pw_signin = input("비밀번호를 입력해주세요: ")
            while True:
                if pw_signin == data[id_signin]:
                    print("로그인되었습니다!")
                    exit_all = True
                    break
                else:
                    pw_signin = input("비밀번호가 틀렸습니다. 다시 입력해주세요: ")
                    continue
                    # while True:
                    #     if pw_signin == data[id_signin]:
                    #         print("로그인되었습니다!")
        if exit_all:
            break
        else:
            print("존재하지 않는 아이디입니다. 다시 입력해주세요")
            continue
        
