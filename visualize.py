import pandas as pd
import matplotlib.pyplot as plt
import stock_data as sd



def visualize(ticker, start_date, end_date):
    plt.rc("font", family="Malgun Gothic")
    dates, prices = sd.closing_price(ticker, start_date, end_date)

    evaluation_total = [(prices[i] * (i+1)) for i in range(len(prices)) ]

    evaluation_total_df = pd.DataFrame({
        'date': dates,
        'closing_price': evaluation_total,
        'principal': 'money'
    })

    fig, ax = plt.subplots()
    
    evaluation_total_df.plot(x='date', y='closing_price', ax=ax, label='평가 금액', color='black')
    ax.set_title(f"{ticker} 평가 금액_")
    ax.set_xlabel('date')
    ax.set_ylabel('평가 금액 ($)')
    ax.tick_params(axis='x', rotation=45, labelsize=5)

    plt.tight_layout()
    plt.show()

p = sd.input_stock()
print(p)
visualize(p, '1800-01-01', '2025-05-30')