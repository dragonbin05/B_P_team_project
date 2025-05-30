import requests
import yfinance as yf
import re

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
        comp = q.get('shortname') or q.get('longname')
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
        company = info.get("shortName") or info.get("longName") or "Unknown"
        return q.upper(), company

    # 2) 회사명 검색
    matches = search_ticker_yahoo(q)
    if matches:
        return matches[0]  # (ticker, company)

    # 3) 못 찾았을 때
    return None

def is_only_english_regex(s: str) -> bool:
    """
    문자열 s가 오직 영어 알파벳 대소문자로만 이루어졌으면 True.
    공백이나 숫자, 특수문자가 하나라도 있으면 False.
    """
    return bool(re.compile(r'^[A-Za-z]+$').fullmatch(s))

def input_stock():
    while True:
        stock_name = input("회사명(영어) 또는 티커(영어)를 입력하세요: ")

        if is_only_english_regex(stock_name) != True: #입력한 문자열이 영어로만 이루어졌는지 확인
          print("영어만 입력하세요.")
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
    
    buy_stock_data = []
    if status == 0:
        print(f'{ticker}를 매수한 날짜, 주당 가격($), 수량을 입력하세요.(ex) 20250530, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    else:
        print(f'{ticker}를 매도한 날짜, 주당 가격($), 수량을 입력하세요.(ex) 20250530, 210, 2.\n종료시 \'exit\' 혹은 \'종료\'를 입력하세요')
    while True:
      input_value = input('날짜, 주당 가격, 수량: ').split(',')
      if input_value == ['exit'] or input_value == ['종료']:
          break
      else:
          date, price, shares = input_value
          date = int(date)
          price = float(price)
          shares = float(shares)
          buy_stock_data.append((status, date, price, shares))

    return buy_stock_data