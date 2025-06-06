# main.py
import member
import id_stock_data
import stock_data
import visualize
import pandas as pd 

def main():
    """프로그램 진입점: 로그인/회원가입 → 메뉴 선택(거래·포트폴리오·시각화)"""
    # ─────────────────────────────
    # 로그인‧회원가입
    # ─────────────────────────────
    member.signup()                   # 로그인 또는 회원가입
    user_id = member.id_signin        # 로그인된 사용자 ID

    # CSV 및 포트폴리오 파일 준비
    id_stock_data.csv_create()                # <user>.csv
    id_stock_data.portfoliocsv_create(user_id)  # port_<user>.csv

    # ─────────────────────────────
    # 메인 메뉴 루프
    # ─────────────────────────────
    while True:
        print("\n===== 메인 메뉴 =====")
        print("1) 거래 내역 입력")
        print("2) 포트폴리오 비중 설정")
        print("3) 시각화")
        print("4) 종료")
        choice = input("선택 >> ")

        # 1) 거래 입력
        if choice == "1":
            print("\n[거래 입력] (exit 입력 시 종료)")
            while True:
                ticker = stock_data.input_stock()
                if ticker.lower() in ["exit", "종료", ""]:
                    break

                # 매수/매도 선택
                status = ""
                while status not in ["buy", "sell"]:
                    status = input("매수(buy) / 매도(sell) 입력 (exit 종료): ").lower()
                    if status in ["exit", "종료", ""]:
                        ticker = ""
                        break
                if not ticker:
                    break

                # 날짜·가격·수량 입력
                rows = stock_data.input_stock_data(ticker, status)
                for row in rows:
                    id_stock_data.csv_update(row)   # 한 줄씩 CSV append

            # 입력 종료 후 날짜순 정렬
            id_stock_data.sort_all_user_files_by_date()
            print("거래 내역 정렬 완료!\n")

        # 2) 포트폴리오 설정
        elif choice == "2":
            print("\n[포트폴리오 설정] (exit 입력 시 종료)")
            id_stock_data.portfolio(user_id)
            print("포트폴리오 설정 완료!\n")

        # 3) 시각화 서브 메뉴
        elif choice == "3":
            while True:
                print("\n--- 시각화 ---")
                print("  a) 설정 포트폴리오 비율(파이)")
                print("  b) 현재 보유 종목별 원금 비중(파이)")
                print("  c) 종목별 원금 vs 평가금액(꺾은선)")
                print("  d) 뒤로")
                sub = input("선택 >> ")

                if sub == "a":
                    visualize.visualize_seted_portfolio(user_id)
                elif sub == "b":
                    visualize.visualize_principal_portfolio(user_id)
                elif sub == "c":
                    sel = visualize.input_visualize_ticker(user_id)
                    df_port = visualize.get_selected_portfolio(user_id, sel)
                    visualize.visualize_stock(df_port)
                elif sub == "d":
                    break
                else:
                    print("잘못된 선택입니다.")

        # 4) 프로그램 종료
        elif choice == "4":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 입력하세요.")

if __name__ == "__main__":
    main()
