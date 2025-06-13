<div align="center">

# 📈 B_P_team_project  
**주식 거래 관리 · 포트폴리오 비중 설정 · 데이터 시각화 통합 솔루션**

<img src="docs/banner.png" width="70%" alt="B_P_team_project Banner">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

> **개인별 주식 거래 입력, 포트폴리오 설정, 오류 자동 감지,  
> 실시간 비율 합계 체크, 데이터 편집,  
> 파이/꺾은선 그래프 시각화까지 한번에!**

---

## 🚀 주요 기능

- **회원가입 / 로그인** : 사용자별 계정 관리
- **거래 입력 & 관리** : 주식 매수/매도 내역 기록, 거래 오류 자동 감지/수정
- **포트폴리오 비중 설정** : 티커별 비율, 합계 100 초과시 경고·즉시 편집
- **CSV 자동 저장** : 각 사용자별 거래/포트폴리오 파일 분리 관리
- **데이터 시각화** : 포트폴리오·보유종목 비율, 평가금액 그래프 제공

---

## 🗂️ 폴더 구조

```
B_P_team_project/
│
├── main.py               # 메인 진입점(전체 메뉴/로직)
├── member.py             # 회원가입/로그인
├── id_stock_data.py      # 거래/포트폴리오 CSV 관리
├── stock_data.py         # 주식 입력/오류 거래 관리
├── visualize.py          # 시각화 함수
├── user_data.json        # 계정 정보
├── <user>.csv            # 거래내역
├── port_<user>.csv       # 포트폴리오 비중
├── requirements.txt      # 필요 라이브러리
└── README.md
```

---

## ⚡️ 빠른 시작

1. **설치**

```bash
git clone https://github.com/dragonbin05/B_P_team_project.git
cd B_P_team_project
pip install -r requirements.txt
```

2. **실행**

```bash
python main.py
```

- 첫 실행시 회원가입 후 로그인
- 메뉴에서 거래 입력/포트폴리오 설정/시각화 선택

---

## 🖥️ 사용법 & 화면 예시

| 메뉴                 | 설명                                                |
|----------------------|-----------------------------------------------------|
| 거래 입력            | 매수/매도 거래 입력, 오류 거래 자동 감지·수정       |
| 포트폴리오 비중 설정 | 티커별 비율, 100 초과시 경고/수정                   |
| 시각화               | 파이차트·꺾은선그래프로 비중·평가금액 확인           |

<details>
<summary>예시 이미지 보기</summary>

<img src="docs/portfolio_example.png" width="400" alt="포트폴리오 비중 예시">
<img src="docs/pie_chart_example.png" width="400" alt="파이차트 예시">

</details>

---

## 🛠️ 사용 기술

- Python 3.10+
- pandas
- matplotlib
- yfinance
- OpenAI (LLM 추천)
- 기타 표준 라이브러리

---

## 🙌 기여 방법

1. **이슈 등록** 또는 **PR 요청** 환영!
2. 버그/기능 추가/사용성 개선 아이디어 자유롭게 남겨주세요.

---

## 📄 라이선스

MIT License  
Copyright (c) 2025

---

<div align="center">

⭐️ **프로젝트가 도움됐다면 Star 한 번 눌러주면 힘이 됩니다!** ⭐️  
문의: [GitHub Issue](https://github.com/dragonbin05/B_P_team_project/issues)

</div>
