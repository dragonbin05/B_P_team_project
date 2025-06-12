import requests
import yfinance as yf
import re
import string
from openai import OpenAI
from datetime import date, datetime
import pandas as pd

def find_company_with_LLM(user_input):
    """
    주어진 user_input(회사 이름이나 잘못된 티커 등)에 대해 LLM을 사용하여
    가장 유사한 공식 회사 이름을 찾아 반환합니다.

    매개변수:
        user_input (str): 사용자가 입력한 잘못된 티커나 회사명.
    반환:
        company_name (str): LLM이 추천하는 정확한 회사명.
    """
    try:
        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        )
        completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[
            {
            "role": 'system',
            "content":"You are an assistant that receives a possibly mistyped ticker symbol, company name, or ETF name. Your job is to identify the single most similar valid investment item and output **exactly** its official “name” (not the ticker), with **no** additional words, explanations, or punctuation—just the name itself."
            },
            {
            "role": "user",
            "content": user_input
            }
        ]
        )
        return completion.choices[0].message.content
    except Exception:
        # 호출 실패 None 반환
        return None

def is_valid_ticker(ticker: str):
    """
    주어진 티커(symbol)가 유효한지 확인합니다.
    yfinance 라이브러리를 사용하여 정보가 존재하는지 검사합니다.S

    매개변수:
        ticker (str): 확인할 티커 문자열.
    반환:
        bool: 유효한 티커이면 True, 아니면 False.
    """
    try:
        info = yf.Ticker(ticker).info
        return bool(info.get("shortName") or info.get("regularMarketPrice"))
    except Exception:
        return False

def search_ticker_yahoo(name: str, max_results: int = 5) -> list[tuple[str,str]]:
    """
    Yahoo Finance 검색 API를 사용하여 입력한 이름(name)에 대해 최대 max_results 만큼
    티커(symbol)와 회사명(longname or shortname)을 반환합니다.

    매개변수:
        name (str): 검색할 회사명 또는 키워드.
        max_results (int): 반환할 최대 결과 개수 (기본값 5).
    반환:
        results (list of tuple): [(symbol, company_name), ...]
    """
    url = 'https://query1.finance.yahoo.com/v1/finance/search'
    params = {'q': name, 'quotesCount': max_results, 'newsCount': 0}
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json().get('quotes') or []
    results = []
    for q in data:
        sym = q.get('symbol')
        comp = q.get('longname') or q.get('shortname') 
        if sym and comp:
            results.append((sym, comp))
    return results

def resolve_to_ticker(query: str):
    """
    사용자가 입력한 query가 티커(symbol)인지, 회사명 키워드인지 판별하고,
    적절한 (ticker, company_name)을 반환합니다.

    1) 입력이 유효한 티커라면 해당 티커와 회사명을 반환
    2) 아니면 Yahoo Finance 검색 결과의 첫 번째 매칭을 반환
    3) 여전히 찾지 못하면 (None, 입력값) 반환

    매개변수:
        query (str): 사용자가 입력한 문자열 (티커 또는 회사명 키워드).
    반환:
        - 유효한 티커라면 (ticker, company_name)
        - 회사명 키워드 검색 결과가 있으면 (ticker, company_name)
        - 둘 다 아니면 (None, query.strip())
    """
    q = query.strip()

    # 1) 이미 티커인지 확인
    if is_valid_ticker(q.upper()):
        info = yf.Ticker(q.upper()).info
        company = info.get("longName") or info.get("shortName") or "Unknown"
        return q.upper(), company

    # 2) 회사명 검색
    matches = search_ticker_yahoo(q)
    if matches:
        return matches[0]  # (ticker, company)

    # 3) 못 찾았을 때
    return (None, q)

def is_only_english_or_special(s: str) -> bool:
    """
    문자열 s가 오직 영어 알파벳(A–Z, a–z),
    ASCII 특수문자(!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~) 그리고 공백(스페이스)로만 이루어졌으면 True.
    숫자, 한글 등 다른 문자가 하나라도 있으면 False.
    """
    PUNCT = re.escape(string.punctuation)  # 특수문자 패턴
    _PATTERN = re.compile(rf'^[A-Za-z{PUNCT} ]+$') # 영어 알파벳 (A–Z, a–z) 혹은 특수문자만 허용
    
    return bool(_PATTERN.fullmatch(s))

def input_stock():
    """
    사용자가 티커 또는 회사명을 입력하도록 요청하고, 올바른 티커로 변환되면 반환합니다.
    1) 사용자가 입력한 문자열이 영어 및 특수문자로만 이루어졌는지 확인
    2) resolve_to_ticker 함수를 통해 유효한 티커인지 판별
    3) 유효 시 "Y/N" 확인 후 최종 티커 반환
    4) 잘못된 입력 시 재입력 요청

    반환:
        ticker (str): 최종 확정된 유효 티커 (대문자).
    """
    while True:
        stock_name = input("종목명(영어) 또는 티커를 입력하세요: ")

        if stock_name.lower() == 'exit':
            return stock_name.lower()
        elif stock_name == '종료':
            return stock_name

        if is_only_english_or_special(stock_name) != True: #입력한 문자열이 영어로만 이루어졌는지 확인
          print("입력을 다시 확인해 주세요.")
          continue

        result = resolve_to_ticker(stock_name)
        if result[0] == None:
            print("입력을 다시 확인해 주세요.")
            LLM = find_company_with_LLM(result[1])
            if LLM == None:
                pass
            else:
                print(f"혹시 {LLM}을(를) 찾나요?")
            continue
        else:
          ticker, company_name = result
          yn = input(f"{ticker}, {company_name}가 맞나요?(Y/N): ").upper()
          if yn == 'Y':
              break
          else:
              continue
          
    return ticker

def is_valid_dateformat(date_str: str) -> bool:
    """
    date_str이 'YYYY-MM-DD' 형식인지 확인합니다.
    - 올바른 예: '2025-06-15', '1999-12-31'
    - 잘못된 예: '2025-6-5', '15-06-2025', '2025/06/15', 'abcd-ef-gh'
    """
    try:
        # 1) 정확히 4자리 연도, 2자리 월, 2자리 일 형태여야 함
        # 2) 예: '2025-06-15'. 만약 '2025-6-5'처럼 앞에 0이 빠지면 오류 발생
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        # 3) 추가 검사: 문자열 전체가 파싱 후에도 동일한지 확인
        #    예: '2025-06-15abc'는 strptime으로 '2025-06-15'까지만 파싱하므로
        #    원본과 parsed.strftime 결과가 다르면 False 처리
        return parsed.strftime("%Y-%m-%d") == date_str
    except ValueError:
        return False

def input_stock_data(ticker, status):
    """
    사용자가 입력한 매수/매도 데이터를 수집하여 리스트로 반환합니다.
    1) status가 'buy'이면 매수, 'sell'이면 매도로 간주.
    2) "exit" 또는 "종료" 입력 시 반복 종료.
    3) 입력 예시: "2025-05-30, 210, 2" -> (ticker, status, date, price, shares)

    매개변수:
        ticker (str): 대상 티커.
        status (str): 'buy' 또는 'sell'.
    반환:
        stock_data (list of tuples): [(ticker, status, date, price, shares), ...]
    """
    stock_data = []
    if status == 'buy':
        print(f'{ticker}를 매수한 날짜, 주당 가격($), 수량을 입력하세요. (ex) 2025-05-30, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    else:
        print(f'{ticker}를 매도한 날짜, 주당 가격($), 수량을 입력하세요. (ex) 2025-05-30, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    while True:
        input_value = input('날짜, 주당 가격, 수량: ')
        
        if input_value == 'exit' or input_value == '종료' or input_value == 'EXIT':
            break
        
        input_value = [x.strip() for x in input_value.split(',')]
        if len(input_value) != 3:
            print("입력을 확인해주세요.")
            continue

        p = input_value[0].split('-')
        q = input_value[0]
        if is_valid_dateformat(q) == False:
            print("날짜를 다시 입력해주세요")
            continue

        today = date.today()
        if int(p[0]) > today.year or int(p[0]) < 2000:
            print("날짜를 다시 입력해주세요. 이 프로그램은 2000년부터 저장 가능합니다.")
            continue
        elif int(p[1]) > 12 or int(p[1]) < 1:
            print("날짜를 다시 입력해주세요")
            continue
        elif int(p[2]) > 31 or int(p[2]) < 1:
            print("날짜를 다시 입력해주세요")
            continue
        elif date.fromisoformat(input_value[0]) > today:
            print("날짜를 다시 입력해주세요")


        date_, price, shares = input_value
        try:
            price = float(price)
            shares = float(shares)
        except ValueError:
            print("입력을 확인해주세요")
            continue
        stock_data.append((ticker, status, date_, price, shares))

    return stock_data

def closing_price(ticker, start_date, end_date):
    """
    yfinance를 사용하여 지정한 기간(start_date ~ end_date)의 일간 종가 데이터를 반환합니다.

    매개변수:
        ticker (str): 조회할 티커.
        start_date (str): 시작 날짜 (YYYY-MM-DD).
        end_date (str): 종료 날짜 (YYYY-MM-DD).
    반환:
        (date_list, close_prices):
            date_list (list of str): 날짜 문자열 목록 ("YYYY-MM-DD").
            close_prices (list of float): 해당 날짜의 종가 리스트.
    """
    ticker = yf.Ticker(ticker) # 1) Ticker 객체 생성

    # 2) 과거 시세 가져오기 (예: 2025-01-01부터 2025-05-30까지)
    hist = ticker.history(
        start=start_date,   # 조회 시작일 (YYYY-MM-DD)
        end=end_date,     # 조회 종료일(이 날짜 이후 데이터는 제외됩니다)
        interval="1d"         # 일간 단위
    )

    # 3) 날짜 리스트와 종가 리스트를 생성
    date_list = [ts.strftime("%Y-%m-%d") for ts in hist.index]
    close_prices = [float(p) for p in hist["Close"].tolist()]

    return date_list, close_prices # (날짜 리스트, 종가 리스트)

def manage_trades(user_id: str):
    """
    CSV 파일(user_id.csv)에서 오류 거래를 정리합니다.

    1) 매도량 > 누적 보유량 거래 목록 출력
    2) 각 거래에 대해: [D]=삭제, [S/Enter]=건너뛰기, [1]=수량 수정, [2]=가격 수정
    3) 수량이 0인 거래는 자동 삭제
    4) 최종 데이터를 원본 CSV에 덮어쓰기
    """
    path = f"{user_id}.csv"
    df = pd.read_csv(path, parse_dates=['date'])

    # 누적 포지션 계산
    df['signed_shares'] = df['shares'] * df['status'].map({'buy': 1, 'sell': -1})
    df['running_position'] = (
        df.groupby('ticker')['signed_shares']
          .cumsum()
          .shift(fill_value=0)
    )

    # 오류 거래 추출
    mask_error = (df['status'] == 'sell') & (df['shares'] > df['running_position'])
    errors = df.loc[mask_error, ['ticker', 'date', 'status', 'shares', 'price']]

    if errors.empty:
        print(f"[manage_trades] '{path}' 파일에 오류 거래가 없습니다.")
    else:
        print(f"[manage_trades] '{path}' 오류 거래 목록:")
        print(errors.to_string(index=True))

        for idx, row in errors.iterrows():
            print(f"\nIndex {idx}: {row['ticker']} on {row['date'].date()} - {row['status']} {row['shares']} @ {row['price']}")
            choice = input("삭제(d), 건너뛰기(s/Enter), 수량 수정(1), 가격 수정(2): ").strip().lower()

            if choice == 'd':
                df.drop(idx, inplace=True)
                print(f"-> Index {idx} deleted.")
            elif choice == '1':
                new_shares = input("New shares: ").strip()
                if new_shares.replace('.', '', 1).isdigit():
                    df.at[idx, 'shares'] = float(new_shares)
                    print(f"-> Shares updated to {new_shares}.")
                else:
                    print("Invalid input. Skipped.")
            elif choice == '2':
                new_price = input("New price: ").strip()
                try:
                    df.at[idx, 'price'] = float(new_price)
                    print(f"-> Price updated to {new_price}.")
                except ValueError:
                    print("Invalid input. Skipped.")
            else:
                print("-> Skipped.")

    # 임시 컬럼 제거 및 수량 0 자동 삭제
    final_df = df.drop(columns=['signed_shares', 'running_position'])
    zero_mask = final_df['shares'] == 0.0
    if zero_mask.any():
        print(f"[manage_trades] 수량 0인 거래 {zero_mask.sum()}건 자동 삭제.")
        final_df = final_df.loc[~zero_mask]

    # 파일 저장
    final_df.to_csv(path, index=False)
    print(f"[manage_trades] '{path}' 파일이 업데이트되었습니다.")