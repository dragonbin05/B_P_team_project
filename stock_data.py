import requests
import yfinance as yf
import re
import string

#써야 하는 함수: input_stock(), input_stock_data(ticker, status), closing_price(ticker, start_date, end_date)
def is_valid_ticker(ticker: str) -> bool:
    try:
        info = yf.Ticker(ticker).info
        return bool(info.get("shortName") or info.get("regularMarketPrice"))
    except Exception:
        return False

def search_ticker_yahoo(name: str, max_results: int = 5) -> list[tuple[str,str]]:
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

def resolve_to_ticker(query: str) -> tuple[str,str] | None:
    """
    - 유효한 티커라면 (ticker, company_name) 반환
    - 회사명 키워드 검색 결과가 있으면 첫 번째 (ticker, company_name) 반환
    - 둘 다 아니면 None 반환
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
    return None

# 재사용 가능한 특수문자 패턴
PUNCT = re.escape(string.punctuation)  

# 영어 알파벳 (A–Z, a–z) 혹은 특수문자만 허용
_PATTERN = re.compile(rf'^[A-Za-z{PUNCT}]+$')

def is_only_english_or_special(s: str) -> bool:
    """
    문자열 s가 오직 영어 알파벳(A–Z, a–z) 또는
    ASCII 특수문자(!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~)로만 이루어졌으면 True.
    숫자, 공백, 한글 등 다른 문자가 하나라도 있으면 False.
    """
    return bool(_PATTERN.fullmatch(s))

def input_stock():
    while True:
        stock_name = input("회사명(영어) 또는 티커를 입력하세요: ")

        if is_only_english_or_special(stock_name) != True: #입력한 문자열이 영어로만 이루어졌는지 확인
          print("입력을 다시 확인해 주세요.")
          continue

        result = resolve_to_ticker(stock_name)
        if result == None:
          print("입력을 다시 확인해 주세요.")
          continue
        else:
          ticker, company_name = result
          yn = input(f"{ticker}, {company_name}가 맞나요?(Y/N): ").upper()
          if yn == 'Y':
              break
          else:
              continue
          
    return ticker

def input_stock_data(ticker, status):
    #매수 status = 'buy'
    #매도 status = 'sell'
    stock_data = []
    if status == 'buy':
        print(f'{ticker}를 매수한 날짜, 주당 가격($), 수량을 입력하세요.(ex) 2025-05-30, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    else:
        print(f'{ticker}를 매도한 날짜, 주당 가격($), 수량을 입력하세요.(ex) 2025-05-30, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    while True:
      input_value = input('날짜, 주당 가격, 수량: ').split(',')
      if input_value == ['exit'] or input_value == ['종료']:
          break
      else:
          date, price, shares = input_value
          price = float(price)
          shares = float(shares)
          stock_data.append((ticker, status, date, price, shares))

    return stock_data

def closing_price(ticker, start_date, end_date):
    ticker = yf.Ticker(ticker) # 1) Ticker 객체 생성

    # 2) 과거 시세 가져오기 (예: 2025-01-01부터 2025-05-30까지)
    hist = ticker.history(
        start=start_date,   # 조회 시작일 (YYYY-MM-DD)
        end=end_date,     # 조회 종료일(이 날짜 이후 데이터는 제외됩니다)
        interval="1d"         # 일간 단위
    )

    # 3) 날짜 리스트와 종가 리스트를 생성
    date_list = [ts.strftime("%Y-%m-%d") for ts in hist.index]
    close_prices = hist["Close"].tolist()

    return date_list, close_prices # (날짜 리스트, 종가 리스트)