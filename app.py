import os
import member
import id_stock_data
import stock_data
import visualize
import pandas as pd 
import streamlit as st

if __name__ == "__main__":
    st.write("# **:red[주식 거래] 및 :green[포트폴리오] 관리 앱**")
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    menu = st.sidebar.radio("메뉴 선택", ["로그인 및 회원가입","거래 내역 입력", "포트폴리오 비중 설정", "시각화"])

    if menu == "로그인 및 회원가입":

        if st.session_state.user_id != None:
            st.success(f"{st.session_state.user_id}로 로그인 상태 유지 중")
            st.write("### :red[로그아웃]하려면 아래의 버튼을 누르세요.")
            logout = st.button("Log out", key="logout_checkbox")

            if logout:
                st.session_state.user_id = None
        else:
            user_id = ""
            user_id = member.signup()         # 로그인된 사용자 ID

            if user_id: #로그인 성공 시 세션에 사용자 ID 저장
                st.session_state.user_id = user_id

            # CSV 및 포트폴리오 파일 준비
                id_stock_data.csv_create()                # <user>.csv
                id_stock_data.portfoliocsv_create(user_id)  # port_<user>.csv
                print(user_id)

            elif user_id != "":
                pass

            else:
                if st.session_state.user_id is None:
                    st.warning("먼저 로그인하세요.")
                    st.stop()

    elif menu == "거래 내역 입력":
        user_id = st.session_state.user_id
        if user_id is None:
            st.warning("먼저 로그인하세요.")
            st.stop()

        st.write("## 거래 내역 입력")
        st.write(f"### 사용자: {user_id}")

        while True:
            ticker = stock_data.input_stock()

            # 매수/매도 선택
            status = st.radio("매수(buy) / 매도(sell) 선택", ("buy", "sell"))

            # 날짜·가격·수량 입력
            rows, click = stock_data.input_stock_data(ticker, status)
            if rows == []:
                break
            for row in rows:
                id_stock_data.csv_update(row)   # 한 줄씩 CSV append

        # 입력 종료 후 날짜순 정렬
        id_stock_data.sort_all_user_files_by_date()

        # 입력 종료 후 거래 오류 내역 수정
        stock_data.manage_trades(user_id)

    elif menu == "포트폴리오 비중 설정":
        user_id = st.session_state.user_id
        if user_id is None:
            st.warning("먼저 로그인하세요.")
            st.stop()

        st.write("# 포트폴리오 비중 설정")
        st.write(f"### 사용자: {user_id}")
        st.write("여기에 포트폴리오 비중 설정 기능을 구현하세요.")
        # 포트폴리오 비중 설정 기능 구현

    elif menu == "시각화":
        user_id = st.session_state.user_id
        if user_id is None:
            st.warning("먼저 로그인하세요.")
            st.stop()

        st.write("# 시각화")
        st.write(f"### 사용자: {user_id}")
        st.write("여기에 시각화 기능을 구현하세요.")
        # 시각화 기능 구현