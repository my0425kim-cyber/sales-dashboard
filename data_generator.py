"""
샘플 판매/매출 데이터 생성 모듈
================================
실제 데이터가 없어도 대시보드를 바로 실행할 수 있도록
가상의 판매 데이터를 생성합니다.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ------------------------------------------------------------------
# 기준 데이터 (카테고리 / 제품 / 지역)
# ------------------------------------------------------------------
CATEGORIES = ["전자기기", "의류", "식품", "가구", "도서"]

PRODUCTS = {
    "전자기기": ["스마트폰", "노트북", "무선이어폰", "스마트워치", "태블릿"],
    "의류":    ["티셔츠", "청바지", "재킷", "운동복", "구두"],
    "식품":    ["커피", "과자", "냉동식품", "음료", "쌀"],
    "가구":    ["책상", "의자", "소파", "침대", "수납장"],
    "도서":    ["소설", "자기계발", "요리", "여행", "IT/컴퓨터"],
}

REGIONS = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]

CHANNELS = ["온라인", "매장", "모바일앱"]


def generate_sales_data(start: str = "2024-01-01",
                        end: str = "2024-12-31",
                        n_rows: int = 5000,
                        seed: int = 42) -> pd.DataFrame:
    """
    지정한 기간 동안의 가상 판매 데이터를 생성합니다.

    Parameters
    ----------
    start, end : str  데이터 기간 (YYYY-MM-DD)
    n_rows     : int  생성할 거래 건수
    seed       : int  재현성을 위한 난수 시드
    """
    rng = np.random.default_rng(seed)

    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    span_days = (end_dt - start_dt).days + 1

    # 주문일자 — 월말/연말 시즌에 매출이 살짝 높아지도록 가중치 부여
    dates = [start_dt + timedelta(days=int(d))
             for d in rng.integers(0, span_days, size=n_rows)]

    categories = rng.choice(CATEGORIES, size=n_rows)
    products = []
    for cat in categories:
        products.append(rng.choice(PRODUCTS[cat]))
    regions = rng.choice(REGIONS, size=n_rows)
    channels = rng.choice(CHANNELS, size=n_rows)

    # 수량 / 단가 — 카테고리별로 단가대가 다르게
    base_price = {
        "전자기기": (50000, 1500000),
        "의류":    (20000, 300000),
        "식품":    (5000, 80000),
        "가구":    (80000, 2000000),
        "도서":    (8000, 45000),
    }
    quantities = rng.integers(1, 10, size=n_rows)
    unit_prices = []
    for cat in categories:
        lo, hi = base_price[cat]
        unit_prices.append(int(rng.integers(lo, hi)))
    unit_prices = np.array(unit_prices)
    quantities = np.array(quantities)
    revenues = unit_prices * quantities

    # 할인율 (0~20%)
    discounts = rng.uniform(0, 0.20, size=n_rows)
    final_revenues = (revenues * (1 - discounts)).round(0).astype(int)

    df = pd.DataFrame({
        "주문ID":    [f"ORD-{100000 + i}" for i in range(n_rows)],
        "주문일자":  dates,
        "카테고리":  categories,
        "제품명":    products,
        "지역":      regions,
        "판매채널":  channels,
        "수량":      quantities,
        "단가":      unit_prices,
        "매출액":    revenues,            # 정가 기준
        "할인율":    (discounts * 100).round(1),
        "최종매출":  final_revenues,      # 할인 반영
    })

    # 주문일자 기준 정렬 후 인덱스 리셋
    df = df.sort_values("주문일자").reset_index(drop=True)
    return df


if __name__ == "__main__":
    # 단독 실행 시 CSV로 저장 (대시보드에서는 이 모듈을 직접 import 사용)
    df = generate_sales_data()
    df.to_csv("sales_data.csv", index=False, encoding="utf-8-sig")
    print(f"샘플 데이터 생성 완료: {len(df):,}건 → sales_data.csv")
    print(df.head())
