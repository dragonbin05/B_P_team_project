import os
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
    user_id = member.signup()         # 로그인된 사용자 ID

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
                if rows == []:
                    break
                for row in rows:
                    id_stock_data.csv_update(row)   # 한 줄씩 CSV append

            # 입력 종료 후 날짜순 정렬
            id_stock_data.sort_all_user_files_by_date()

            # 입력 종료 후 거래 오류 내역 수정
            stock_data.manage_trades(user_id)

        # 2) 포트폴리오 설정
        elif choice == "2":
            print("\n[포트폴리오 설정] (exit 입력 시 종료)")
            id_stock_data.portfolio(user_id)
            print("포트폴리오 설정 완료!\n")

            # main.py의 포트폴리오 설정 뒤에 아래 코드 추가
            if __name__ == "__main__":
                # ... 기존 main 함수 실행 ...
                # 예시로 아래만 따로 실행하려면 user_id 변수 직접 할당해도 됨
                # user_id = "test" 등
                id_stock_data.check_and_edit_portfolio_ratio(user_id)
                id_stock_data.remove_zero_ratio_rows(user_id)

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
                    # ‘port_{user_id}.csv’ 에 설정된 포트폴리오 데이터가 있는지 확인
                    port_path = f"port_{user_id}.csv"
                    # 파일이 없거나, 헤더만 있고 실제 데이터가 없으면 스킵
                    if not os.path.isfile(port_path):
                        print("포트폴리오 파일이 존재하지 않습니다. 먼저 포트폴리오를 설정하세요.")
                        continue
                    df_port = pd.read_csv(port_path)
                    # 헤더만 있고 실제 데이터(티커·ratio) 컬럼이 비어 있으면 스킵
                    if df_port.shape[0] == 0 or "ticker" not in df_port.columns or df_port["ticker"].isnull().all():
                        print("저장된 포트폴리오 데이터가 없습니다. 먼저 포트폴리오를 설정하세요.")
                        continue

                    # 실제 데이터가 있으면 시각화 함수 호출
                    visualize.visualize_seted_portfolio(user_id)

                elif sub == "b":
                    visualize.visualize_principal_portfolio(user_id)

                elif sub == "c":
                    # 보유 종목이 있는지 먼저 확인
                    # get_principal_and_position을 통해
                    # date별 position을 계산해 보유 여부 판단
                    all_tickers = pd.read_csv(f"{user_id}.csv")["ticker"].unique()
                    having_any = False

                    for tk in all_tickers:
                        df_t = visualize.get_principal_and_position(user_id, tk)
                        # 맨 마지막 position(=0이 아니면 보유 중)
                        if not df_t.empty and df_t["position"].iloc[-1] > 0:
                            having_any = True
                            break

                    if not having_any:
                        print("현재 한 주도 보유하지 않고 있습니다. 시각화할 수 없습니다.")
                        continue

                    # 보유 종목이 하나 이상 있으면 티커 선택으로 넘어감
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
