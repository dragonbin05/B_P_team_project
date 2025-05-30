import stock_data
import id_stock_data
import member

def main():

    member.signup()
    id_stock_data.csv_create()
    for i in stock_data.input_stock_data('AAPL', 'buy'):
        id_stock_data.csv_update(i)

if __name__ == '__main__':
    main()