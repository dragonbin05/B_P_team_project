import re
import csv
import os

# 특수문자 존재하면 True 반환
def contains_special_char(s): 
    return bool(re.search(r'[^a-zA-Z0-9\s]', s)) # 특수문자를 의미하는 정규표현식: 알파벳, 숫자, 공백을 제외한 문자

def signup():
    while True:
        id = input("ID를 입력하시오: ")
    
        with open("user_Data.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            usernames = [row["username"] for row in reader]

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

            # 파일이 없으면 헤더 추가, 있으면 헤더 없이 이어서 저장
            file_exists = os.path.isfile("user_data.csv")

            with open("user_data.csv", mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(["username", "password"])  # 헤더 작성

                writer.writerow([id, pw])  # 사용자 정보 저장

            print("회원가입이 완료되었습니다.")
            break

signup()