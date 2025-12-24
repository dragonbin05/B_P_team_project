import requests
import yfinance as yf
import re
import string
from openai import OpenAI
from datetime import date, datetime
import pandas as pd
import streamlit as st
from datetime import date, datetime

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
        api_key="<OPENROUTER_API_KEY>",
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
    stock_name = ""
    stock_name = st.text_input("종목명(영어) 또는 티커를 입력하세요.")

    if is_only_english_or_special(stock_name) != True: #입력한 문자열이 영어로만 이루어졌는지 확인
        st.warning("입력을 다시 확인해 주세요.")

    result = resolve_to_ticker(stock_name)
    if result[0] == None:
        st.warning("입력을 다시 확인해 주세요.")
        LLM = find_company_with_LLM(result[1])
        if LLM == None:
            pass
        else:
            st.write(f"혹시 {LLM}을(를) 찾나요?")
    else:
        ticker, company_name = result
        st.write(f"### {ticker}, {company_name}가 맞나요?")
        yn = st.button("Yes")

        if yn:
            return ticker
        else:
            st.warning("아닌 경우, 티커를 다시 입력하세요.")

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


def is_valid_dateformat(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def input_stock_data(ticker: str, status: str, key_prefix: str = "tx"):
    """
    Streamlit 환경에서 주식 거래(매수/매도) 내역을 입력받아 세션에 누적 저장하는 함수이다.

    사용자는 거래 날짜를 YYYYMMDD 형식으로 입력하며,
    내부적으로 날짜의 유효성을 검증한 후 YYYY-MM-DD 형식으로 변환하여 저장한다.
    입력은 여러 줄로 가능하며, 각 줄은 하나의 거래를 의미한다.

    입력 형식:
        YYYYMMDD, price, shares
        예) 20250530, 210, 2

    주요 기능:
    1. ticker와 status(buy/sell)에 따라 고유한 session_state 키를 생성하여
       거래 내역을 세션 단위로 유지한다.
    2. 여러 줄 입력을 받아 각 줄을 파싱하고 형식·날짜·숫자 유효성을 검증한다.
    3. 날짜는 2000년 이후이면서 미래 날짜가 아닌 경우만 허용한다.
    4. 유효한 입력만 (ticker, status, date, price, shares) 형태의 튜플로 저장한다.
       이때 date는 ISO 형식(YYYY-MM-DD)으로 변환되어 저장된다.
    5. 현재까지 누적된 거래 내역을 표 형태로 화면에 표시한다.
    6. '완료(Done)' 버튼 클릭 여부를 함께 반환하여 이후 로직(저장, 페이지 전환 등)에 활용할 수 있다.

    매개변수:
        ticker (str): 거래 대상 주식의 티커(symbol)
        status (str): 거래 유형 ('buy' 또는 'sell')
        key_prefix (str): session_state 키 구분을 위한 접두사

    반환값:
        Tuple[list[tuple], bool]:
            - 거래 내역 리스트
              [(ticker, status, 'YYYY-MM-DD', price, shares), ...]
            - 완료 버튼 클릭 여부 (True / False)
    """
    state_key = f"{key_prefix}_{ticker}_{status}"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    action_kr = "매수" if status == "buy" else "매도"
    st.subheader(f"{ticker} {action_kr} 내역 입력")

    st.info(
        "형식(format): YYYYMMDD, price, shares\n"
        "예: 20250530, 210, 2\n"
        "여러 건은 줄바꿈(newline)으로 입력하세요."
    )

    raw = st.text_area(
        "거래 내역(여러 줄 입력 가능)",
        placeholder="20250530, 210, 2\n20250601, 205.5, 1",
        key=f"{state_key}_textarea",
        height=120,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        add_clicked = st.button("추가(Add)", key=f"{state_key}_add")
    with col2:
        clear_clicked = st.button("초기화(Clear)", key=f"{state_key}_clear")
    with col3:
        done_clicked = st.button("완료(Done)", key=f"{state_key}_done")

    if clear_clicked:
        st.session_state[state_key] = []
        st.success("입력 내역을 초기화했습니다.")

    if add_clicked:
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if not lines:
            st.warning("입력값이 비어 있습니다.")
        else:
            today = date.today()
            added = 0

            for idx, ln in enumerate(lines, start=1):
                parts = [x.strip() for x in ln.split(",")]
                if len(parts) != 3:
                    st.error(f"{idx}번째 줄 형식 오류: '{ln}'")
                    continue

                date_raw, price_s, shares_s = parts

                # 날짜 형식 검증 (YYYYMMDD)
                if len(date_raw) != 8 or not date_raw.isdigit():
                    st.error(f"{idx}번째 줄 날짜 형식 오류: {date_raw} (YYYYMMDD)")
                    continue

                y, m, d = int(date_raw[:4]), int(date_raw[4:6]), int(date_raw[6:8])

                # 실제 날짜 유효성 검사
                try:
                    dt = date(y, m, d)
                except ValueError:
                    st.error(f"{idx}번째 줄 날짜 오류: {date_raw}")
                    continue

                if y < 2000 or dt > today:
                    st.error(f"{idx}번째 줄 날짜 범위 오류: {date_raw}")
                    continue

                # YYYY-MM-DD로 변환
                date_iso = dt.isoformat()

                # 숫자 변환
                try:
                    price = float(price_s)
                    shares = float(shares_s)
                except ValueError:
                    st.error(f"{idx}번째 줄 숫자 오류: price={price_s}, shares={shares_s}")
                    continue

                # 저장은 ISO 형식
                st.session_state[state_key].append(
                    (ticker, status, date_iso, price, shares)
                )
                added += 1

            if added > 0:
                st.success(f"{added}건이 추가되었습니다.")

    if st.session_state[state_key]:
        st.write("현재 누적된 거래 내역:")
        st.dataframe(
            [
                {"ticker": t, "status": s, "date": ds, "price": p, "shares": sh}
                for (t, s, ds, p, sh) in st.session_state[state_key]
            ],
            use_container_width=True,
        )
    else:
        st.info("아직 추가된 내역이 없습니다.")

    return st.session_state[state_key], done_clicked

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