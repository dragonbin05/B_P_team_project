import re

id = input("ID를 입력하시오: ")
print("Password는 영어 소문자, 숫자, 특수기호를 사용할 수 있으며, 특수기호는 적어도 한 개 이상 사용해야 합니다.")
pw = input("Password를 입력하시오: ")

def contains_special_char(s):
    # 특수문자를 의미하는 정규표현식: 알파벳, 숫자, 공백을 제외한 문자
    return bool(re.search(r'[^a-zA-Z0-9\s]', s))

while contains_special_char(pw) == False:
    pw = input("특수문자를 포함해서 Password를 다시 적어주세요")
    if contains_special_char(pw) == True:
        break