import stock_data 
import id_stock_data
import member

def main():
    member.signup()
    id_stock_data.csv_create()
    id_stock_data.csv_update(stock_data.resolve_to_ticker())

if __name__ == '__main__':
    main()