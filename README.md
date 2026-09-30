# 📊 판매/매출 분석 대시보드

Streamlit으로 만든 인터랙티브 판매/매출 분석 대시보드입니다.
동료들과 웹 링크 하나로 공유할 수 있습니다.

## ✨ 주요 기능
- **KPI 카드** — 총 매출, 주문 건수, 판매 수량, 객단가
- **월별 매출 추이** — 라인 차트
- **카테고리별 / 지역별 / 채널별 매출** — 막대·파이 차트
- **Top 10 제품** — 수평 막대 차트
- **상세 거래 내역 테이블** + CSV 다운로드
- **사이드바 필터** — 기간, 카테고리, 지역, 판매채널

## 🚀 로컬에서 실행

```bash
# 1. 가상환경 생성 및 활성화 (권장)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # macOS/Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 대시보드 실행
streamlit run app.py
```

브라우저가 자동으로 `http://localhost:8501` 에 열립니다.

## 📁 프로젝트 구조
```
고니/
├── app.py                # 메인 Streamlit 대시보드
├── data_generator.py     # 샘플 판매 데이터 생성
├── requirements.txt      # 의존성
└── .streamlit/
    └── config.toml       # Streamlit 테마 설정
```

## 🔧 실제 데이터로 교체하기
`app.py` 의 `load_data()` 함수를 아래처럼 수정하면 됩니다.

```python
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("my_sales.csv", parse_dates=["주문일자"])
    df["연월"] = df["주문일자"].dt.to_period("M").astype(str)
    return df
```

컬럼명은 다음과 같이 맞춰주세요:
`주문ID, 주문일자, 카테고리, 제품명, 지역, 판매채널, 수량, 단가, 할인율, 최종매출`

## 🌐 동료와 공유하기 (3가지 방법)

### 1) Streamlit Community Cloud (무료, 권장)
1. 이 프로젝트를 GitHub 퍼블릭 리포지토리에 push
2. https://share.streamlit.io 접속 → GitHub 계정 연결
3. "New app" 선택 → 리포지토리/브랜치/Main file path(`app.py`) 지정
4. 배포 완료 시 `https://<app>.streamlit.app` 링크 발급 → 동료에게 공유

### 2) 로컬 네트워크 공유 (사내망)
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
같은 와이파이/망의 동료가 `http://<내IP>:8501` 로 접속

### 3) 임시 공유 (ngrok)
```bash
ngrok http 8501
```
발급된 공개 URL을 동료에게 전달 (PC가 켜져 있을 때만 유효)

## 🛠 기술 스택
- [Streamlit](https://streamlit.io) — 대시보드 프레임워크
- [Pandas](https://pandas.pydata.org) — 데이터 처리
- [Plotly](https://plotly.com/python) — 인터랙티브 차트
