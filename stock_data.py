import requests
import yfinance as yf

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
        return matches[0]  # (symbol, company)

    # 3) 못 찾았을 때
    return None