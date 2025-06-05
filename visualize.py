import pandas as pd
import matplotlib.pyplot as plt
import stock_data as sd

def one_visualize(user_id, ticker):
    plt.rc("font", family="Malgun Gothic") #한글 깨짐 방지

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

    fig, ax = plt.subplots()
    
    stock_data.plot(x='date', y='principal', ax=ax, label='원금', color='black')
    stock_data.plot(x='date', y='valuation', ax=ax, label='평가금액', color='blue')
    ax.set_title(f"{ticker} 원금, 평가금액")
    ax.set_xlabel('date')
    ax.set_ylabel('달러($)')
    ax.tick_params(axis='x', rotation=45, labelsize=5)

    plt.tight_layout()
    plt.show()

# one_visualize('test', 'AVGO')