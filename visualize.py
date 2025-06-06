import pandas as pd
import matplotlib.pyplot as plt
import stock_data as sd
from functools import reduce

def get_principal_and_position(user_id: str, ticker: str):
    """
    principal = 현재 포지션의 순 원가만 반영 (차익·손실 제외)
                ⇒ 포지션 0이면 principal 0
    반환 컬럼: date, principal, position, close, valuation
    """
    import pandas as pd
    import stock_data  # closing_price 함수가 여기 있다고 가정

    # 1) 해당 티커 거래 내역 읽기 (날짜 오름차순)
    df = (
        pd.read_csv(f"{user_id}.csv", parse_dates=["date"])
          .query("ticker == @ticker")
          .sort_values("date")
          .reset_index(drop=True)
    )

    principal = 0.0        # 누적 원가
    position  = 0.0        # 누적 보유 수
    principals, positions = [], []

    # 2) 거래 행별로 principal / position 업데이트
    for _, row in df.iterrows():
        price, shares = row["price"], row["shares"]

        if row["status"] == "buy":
            principal += price * shares
            position  += shares

        else:  # sell
            if position == 0:
                # 보유 수량 0인데 매도 기록 → 무시
                print(f"[무시] {row['date'].date()} {ticker} 매도, 보유 0주")
                principals.append(principal)
                positions.append(position)
                continue

            shares_to_sell = min(shares, position)
            avg_cost = principal / position        # position>0 보장
            principal -= avg_cost * shares_to_sell
            position  -= shares_to_sell

        # 포지션 0이면 principal도 0으로 정리(부동소수점 오차 방지)
        if position == 0:
            principal = 0.0

        principals.append(principal)
        positions.append(position)

    df["principal"] = principals
    df["position"]  = positions

    # 3) 종가 불러와 merge → valuation 계산
    start = df["date"].min().strftime("%Y-%m-%d")
    end   = pd.Timestamp.today().strftime("%Y-%m-%d")
    dates, prices = stock_data.closing_price(ticker, start, end)

    close_df = pd.DataFrame(
        {"date": pd.to_datetime(dates), "close": prices}
    )

    df = df.merge(close_df, on="date", how="left")
    df["close"] = df["close"].ffill().fillna(0)
    df["valuation"] = df["position"] * df["close"]

    return df[["date", "principal", "position", "close", "valuation"]]


def input_visualize_ticker(user_id):
    """
    사용자(user_id)의 거래 기록에서 보유 중인 티커 목록을 출력하고,
    시각화할 티커를 입력받아 반환합니다.
    • "전체" 또는 "all" 입력 시 모든 티커 반환
    • 쉼표(',')로 구분하여 여러 티커 입력 가능 (공백 무시, 대소문자 구분 없음)

    반환:
        selected_ticker (list of str) - 선택된 티커 리스트
    """
    ticker_col = pd.read_csv(f"{user_id}.csv")["ticker"]
    tickers = list(ticker_col.unique())
    while True:
        k = 1
        for i in tickers:
            print(f"{k}. {i}")
            k += 1
        print("시각화를 원하는 종목의 티커 또는 전체(all)를 입력하세요(영어 대소문자 상관없음). (ex1)aapl, tsla / (ex2)전체 / (ex3)all")
        selected_ticker = input()
        if selected_ticker == "전체" or selected_ticker.upper() =='ALL': #전체 선택이면 tickers리스트 그냥 사용
            selected_ticker = tickers
            break
        else:
            selected_ticker = [item.strip().upper() for item in selected_ticker.split(",")]
            for i in selected_ticker:
                if i in tickers:
                    pass
                else:
                    print(f"{i}은(는) 보유하고 있지 않습니다. 다시 입력하세요.")
                    continue
            break

    return selected_ticker

def get_selected_portfolio(user_id, selected_ticker) -> pd.DataFrame:
    """
    선택된 티커 리스트(selected_ticker)에 대해 각 티커별로
    get_principal_and_position 함수를 호출하여 반환된 DataFrame들을
    날짜별(date 인덱스)로 합쳐(total outer join),
    "total_principal"과 "total_valuation" 컬럼을 계산하여 반환합니다.

    반환 컬럼:
        date               (datetime64[ns])
        total_principal    (float) - 모든 티커 원금 합계
        total_valuation    (float) - 모든 티커 평가금액 합계
    """
    per_ticker_dfs = []

    for ticker in selected_ticker:
        #티커별로 DataFrame 얻기
        df = get_principal_and_position(user_id, ticker)

        #'date'를 인덱스로, 'principal'과 'valuation'만 추출
        df = df.set_index("date")[["principal", "valuation"]]

        #컬럼 이름을 "{ticker}_principal", "{ticker}_valuation"으로 변경
        df = df.rename(
            columns={
                "principal": f"{ticker}_principal",
                "valuation": f"{ticker}_valuation"
            }
        )

        per_ticker_dfs.append(df)

    #모든 티커 DataFrame을 'date' 인덱스를 기준으로 outer join
    #(reduce를 사용해 순차적으로 병합)
    df_merged = reduce(
        lambda left, right: pd.merge(
            left, right,
            how="outer",
            left_index=True,
            right_index=True
        ),
        per_ticker_dfs
    )

    #거래가 없는 날(해당 티커 컬럼이 NaN인 경우)을 0으로 채우기
    df_merged = df_merged.fillna(0)

    #"총 누적 원금"과 "총 평가금액" 계산
    #-> principal 관련 컬럼들만 골라서 합계
    principal_cols = [col for col in df_merged.columns if col.endswith("_principal")]
    valuation_cols = [col for col in df_merged.columns if col.endswith("_valuation")]

    df_merged["total_principal"] = df_merged[principal_cols].sum(axis=1)
    df_merged["total_valuation"] = df_merged[valuation_cols].sum(axis=1)

    #최종 반환용 DataFrame: date 인덱스를 일반 컬럼으로 돌리고, 
    #total_principal·total_valuation만 남기기
    result = df_merged.reset_index()[["date", "total_principal", "total_valuation"]]

    return result

def visualize_stock(edited_stock_data):
    """
    날짜별로 "원금(total_principal)"과 "평가금액(total_valuation)"을 꺾은선 그래프로 표시합니다.

    매개변수:
        edited_stock_data (DataFrame) - get_selected_portfolio 반환 DataFrame
    """
    plt.rc("font", family="Malgun Gothic") #한글 깨짐 방지

    fig, ax = plt.subplots()
    edited_stock_data.plot(x='date', y='total_principal', ax=ax, label='원금', color='black')
    edited_stock_data.plot(x='date', y='total_valuation', ax=ax, label='평가금액', color='blue')
    ax.set_title("원금, 평가금액")
    ax.set_xlabel('date')
    ax.set_ylabel('달러($)')
    ax.tick_params(axis='x', rotation=45, labelsize=10)

    plt.tight_layout()
    plt.show()

def visualize_seted_portfolio(user_id):
    """
    "port_{user_id}.csv" 파일에 저장된 사용자 포트폴리오 비율을 파이 차트로 시각화합니다.

    예시 CSV 포맷:
        ticker,ratio
        AAPL,30
        TSLA,20
        MSFT,50

    반환: 없음 (그래프를 출력)
    """
    port_data = pd.read_csv(f"port_{user_id}.csv")

    # “ticker” 컬럼을 인덱스로, “ratio” 컬럼을 파이 차트값으로 사용
    port_data = port_data.set_index("ticker")
    ratio = port_data["ratio"]

    # 파이 차트 그리기
    plt.rc("font", family="Malgun Gothic")  # 한글 깨짐 방지
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        ratio,
        labels=ratio.index,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 10}
    )
    ax.set_title("설정 포트폴리오 비율", fontsize=14)
    ax.axis("equal")  # 원형 파이로 그리기

    plt.tight_layout()
    plt.show()

def visualize_principal_portfolio(user_id):
    """
    user_id.csv에 기록된 거래 내역을 통해, 현재 보유 중인(포지션>0) 종목들의
    '지금까지 순투자된 원금(net principal)'을 구해서 파이 차트로 시각화합니다.
    """
    # CSV에서 중복 없는 ticker 리스트 추출
    df_all = pd.read_csv(f"{user_id}.csv", parse_dates=["date"])
    tickers = list(df_all["ticker"].unique())

    # 각 티커별로 가장 최근 principal 값만 뽑아서 딕셔너리에 저장
    principal_for_pie = {}
    for ticker in tickers:
        df_t = get_principal_and_position(user_id, ticker)

        # position 컬럼을 마지막으로 확인하여 “오늘 보유 수량 > 0”인 종목만 대상
        last_row = df_t.iloc[-1]
        if last_row["position"] > 0:
            principal_for_pie[ticker] = last_row["principal"]
        # position == 0 이면 이미 전부 팔았거나 보유 수량이 없으므로 제외

    # 보유 중인 종목이 하나도 없는 경우 예외 처리
    if not principal_for_pie:
        print("현재 보유 중인 종목이 없습니다.")
        return

    # 파이 차트에 사용할 라벨과 사이즈 준비
    labels = list(principal_for_pie.keys())
    sizes  = list(principal_for_pie.values())

    # 파이 차트 그리기
    plt.rc("font", family="Malgun Gothic")  #한글 깨짐 방지
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 10}
    )
    ax.set_title("현재 보유 종목별 순투자 원금 비중", fontsize=12)
    ax.axis("equal")  # 파이를 원형으로 그리기 위해
    plt.tight_layout()
    plt.show()

# visualize_principal_portfolio('test')

# p = input_visualize_ticker('test')
# q = get_selected_portfolio('test', p)
# visualize_stock(q)