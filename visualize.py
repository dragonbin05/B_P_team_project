import pandas as pd
import matplotlib.pyplot as plt
import stock_data as sd
from functools import reduce

def get_principal_and_position(user_id, ticker):
    stock_data = pd.read_csv(f"{user_id}.csv", parse_dates=["date"])
    stock_data = stock_data[stock_data['ticker'] == ticker] #티커에 맞는 행만 남기기

    #전 거래일 기준 원금 편차 구하기
    stock_data["cash_flow"] = stock_data.apply(
        lambda r:  r["price"] * r["shares"] if r["status"] == "buy"
                else -r["price"] * r["shares"],
        axis=1
    )
    stock_data["principal"] = stock_data["cash_flow"].cumsum() #누적합을 'principal'컬럼에 저장

    #position(보유 주식 수) 계산: 매수면 +shares, 매도면 –shares
    stock_data["delta_shares"] = stock_data.apply(
        lambda r:  r["shares"] if r["status"] == "buy"
                else -r["shares"],
        axis=1
    )
    stock_data["position"] = stock_data["delta_shares"].cumsum() #누적합을 'position'컬럼에 저장

    #날짜별 마지막 principal·position 값만 남기기
    stock_data = stock_data.groupby("date", as_index=False).agg({
        "principal": "last",
        "position": "last"
    })
    

    #전체 날짜 범위 생성 (첫 거래일 ~ 현재 날짜 사이, 매일 1일 간격)
    start_date = stock_data["date"].min()
    end_date = pd.Timestamp.today().normalize()
    full_date_index = pd.date_range(start=start_date, end=end_date, freq="D")
    full_dates = pd.DataFrame({"date": full_date_index})

    stock_data = full_dates.merge(stock_data, on="date", how="left")
    stock_data["principal"] = stock_data["principal"].ffill() #없던 날짜와 값 추가
    stock_data["position"] = stock_data["position"].ffill() #없던 날짜와 값 추가

    close_dates, close_prices = sd.closing_price(ticker, start_date, end_date) #종가 불러오기

    close_dates = pd.to_datetime(close_dates)
    price_df = pd.DataFrame({
        "date": close_dates,
        "close": close_prices
    })

    stock_data = stock_data.merge(price_df, on="date", how="left") #“stock_data”에 종가 데이터를 병합
    stock_data["close"] = stock_data["close"].ffill().fillna(0) #종가가 NaN인 날(※거래소 휴장일 등)은 직전 종가로 채우기(ffill) + 매매 개시 이전엔 0으로 채움
    stock_data["valuation"] = stock_data["position"] * stock_data["close"] #평가 금액(valuation) 계산: “보유 주식 수 × 종가”

    result = stock_data[["date", "principal", "valuation"]]
    return stock_data

def input_visualize_ticker(user_id):
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
    한 사람(user_id)이 보유한 여러 종목(tickers)의 DataFrame을 합쳐,
    날짜별로 '총 누적 원금(total_principal)'과 '총 평가금액(total_valuation)'을 계산해 반환합니다.

    반환 컬럼:
        date             (datetime64[ns])
        total_principal  (float)  → 여러 티커의 principal 합계
        total_valuation  (float)  → 여러 티커의 valuation 합계
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

def visualize(edited_stock_data):
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