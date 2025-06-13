import re
from pathlib import Path
import json

# 특수문자 존재하면 True 반환!
def contains_special_char(s):
    """
    문자열에 특수문자가 포함되어 있는지 확인하는 함수.

    Args:
        s (str): 검사할 문자열

    Returns:
        bool: 특수문자가 하나라도 포함되어 있으면 True, 아니면 False
    """
    return bool(re.search(r'[^a-zA-Z0-9\s]', s)) # 특수문자를 의미하는 정규표현식: 알파벳, 숫자, 공백을 제외한 문자

id_signin = ''
data = {}

def signup():
    """
    사용자에게 회원가입 또는 로그인을 선택하게 하고, 회원가입/로그인 로직을 처리하는 함수.

    Returns:
        str: 로그인(또는 회원가입 후 자동 로그인)한 사용자의 ID

    기능:
        - user_data.json 파일에서 사용자 정보를 읽어옴.
        - 'Y' 입력 시 로그인, 'N' 입력 시 회원가입 절차 진행.
        - 회원가입 시 ID 중복 체크, 비밀번호에 특수문자 포함 검증, user_data.json에 정보 저장.
        - 회원가입이 끝나면 자동으로 로그인 상태가 됨.
        - 잘못된 입력은 다시 입력하도록 안내.
    """
    global id_signin
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
            id = signin()
            return id
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

            print("회원가입이 완료되었습니다!")
            # —> 새로 만든 ID를 곧바로 로그인 상태로 설정
            id_signin = id
            print(f"자동으로 '{id}' 계정에 로그인되었습니다.")
            return id


def signin():
    """
    사용자에게 아이디와 비밀번호를 입력받아 로그인 절차를 진행하는 함수.

    Returns:
        str: 로그인에 성공한 사용자의 ID

    기능:
        - user_data.json 파일에서 사용자 정보를 읽어옴.
        - 아이디와 비밀번호가 일치하면 로그인 성공, 아니면 계속 재입력 요청.
        - 없는 아이디 입력 시 다시 입력 안내.
        - 로그인에 성공하면 해당 ID를 반환.
    """
    global id_signin
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
        if exit_all:
            return id_signin
        else:
            print("존재하지 않는 아이디입니다. 다시 입력해주세요")
            continue
        
