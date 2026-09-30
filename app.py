"""
판매/매출 분석 대시보드 (Streamlit)
==================================
실행:  streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from data_generator import generate_sales_data

# ------------------------------------------------------------------
# 페이지 설정
# ------------------------------------------------------------------
st.set_page_config(
    page_title="판매/매출 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------
# 데이터 로드 (캐싱)
# ------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = generate_sales_data()
    df["주문일자"] = pd.to_datetime(df["주문일자"])
    df["연월"] = df["주문일자"].dt.to_period("M").astype(str)
    return df


df_all = load_data()

# ------------------------------------------------------------------
# 사이드바 — 필터
# ------------------------------------------------------------------
st.sidebar.title("⚙️ 필터")

min_date = df_all["주문일자"].min().to_pydatetime()
max_date = df_all["주문일자"].max().to_pydatetime()
date_range = st.sidebar.date_input(
    "조회 기간",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

sel_categories = st.sidebar.multiselect(
    "카테고리", df_all["카테고리"].unique(), default=list(df_all["카테고리"].unique()))
sel_regions = st.sidebar.multiselect(
    "지역", df_all["지역"].unique(), default=list(df_all["지역"].unique()))
sel_channels = st.sidebar.multiselect(
    "판매채널", df_all["판매채널"].unique(), default=list(df_all["판매채널"].unique()))

# ------------------------------------------------------------------
# 필터 적용
# ------------------------------------------------------------------
mask = (
    (df_all["주문일자"] >= pd.Timestamp(start_d))
    & (df_all["주문일자"] <= pd.Timestamp(end_d))
    & (df_all["카테고리"].isin(sel_categories))
    & (df_all["지역"].isin(sel_regions))
    & (df_all["판매채널"].isin(sel_channels))
)
df = df_all.loc[mask].copy()

# ------------------------------------------------------------------
# 타이틀
# ------------------------------------------------------------------
st.title("📊 판매/매출 분석 대시보드")
st.caption(f"조회 기간: {start_d} ~ {end_d}  |  거래 건수: {len(df):,}건")

if df.empty:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다. 필터를 다시 확인해주세요.")
    st.stop()

# ------------------------------------------------------------------
# KPI 카드
# ------------------------------------------------------------------
total_rev = int(df["최종매출"].sum())
total_orders = df["주문ID"].nunique()
avg_order = int(df["최종매출"].sum() / total_orders) if total_orders else 0
total_qty = int(df["수량"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 총 매출", f"{total_rev:,}원")
c2.metric("🧾 주문 건수", f"{total_orders:,}건")
c3.metric("📦 판매 수량", f"{total_qty:,}개")
c4.metric("💵 객단가", f"{avg_order:,}원")

st.divider()

# ------------------------------------------------------------------
# 월별 매출 추이
# ------------------------------------------------------------------
st.subheader("📈 월별 매출 추이")
monthly = (df.groupby("연월", as_index=False)
             .agg(매출=("최종매출", "sum"), 주문건수=("주문ID", "nunique"))
             .sort_values("연월"))
fig_trend = px.line(
    monthly, x="연월", y="매출",
    markers=True, text="매출",
    template="plotly_white",
    labels={"연월": "월", "매출": "매출(원)"},
)
fig_trend.update_traces(textposition="top center", texttemplate="%{text:,.0f}")
fig_trend.update_layout(height=380, hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

# ------------------------------------------------------------------
# 카테고리별 / 지역별 매출 (2단)
# ------------------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🏷️ 카테고리별 매출")
    cat_rev = (df.groupby("카테고리", as_index=False)
                 .agg(매출=("최종매출", "sum"))
                 .sort_values("매출", ascending=True))
    fig_cat = px.bar(cat_rev, x="매출", y="카테고리", orientation="h",
                     template="plotly_white", text="매출",
                     labels={"매출": "매출(원)"})
    fig_cat.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_cat.update_layout(height=360, yaxis_title="")
    st.plotly_chart(fig_cat, use_container_width=True)

with col_b:
    st.subheader("🗺️ 지역별 매출 비중")
    region_rev = (df.groupby("지역", as_index=False)
                    .agg(매출=("최종매출", "sum"))
                    .sort_values("매출", ascending=False))
    fig_reg = px.pie(region_rev, values="매출", names="지역",
                     hole=0.4, template="plotly_white")
    fig_reg.update_traces(textposition="inside", textinfo="label+percent")
    fig_reg.update_layout(height=360, showlegend=False)
    st.plotly_chart(fig_reg, use_container_width=True)

# ------------------------------------------------------------------
# 채널별 매출 + Top 제품
# ------------------------------------------------------------------
col_c, col_d = st.columns([1, 2])

with col_c:
    st.subheader("📡 채널별 매출")
    ch_rev = (df.groupby("판매채널", as_index=False)
                .agg(매출=("최종매출", "sum"))
                .sort_values("매출", ascending=False))
    fig_ch = px.bar(ch_rev, x="판매채널", y="매출", template="plotly_white",
                    text="매출", labels={"매출": "매출(원)"})
    fig_ch.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_ch.update_layout(height=360, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_ch, use_container_width=True)

with col_d:
    st.subheader("🏆 매출 Top 10 제품")
    top_prod = (df.groupby("제품명", as_index=False)
                  .agg(매출=("최종매출", "sum"), 수량=("수량", "sum"))
                  .sort_values("매출", ascending=False)
                  .head(10))
    fig_top = px.bar(top_prod, x="매출", y="제품명", orientation="h",
                     template="plotly_white", text="매출",
                     labels={"매출": "매출(원)", "제품명": ""})
    fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_top.update_layout(height=360, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_top, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# 상세 데이터 테이블
# ------------------------------------------------------------------
st.subheader("📋 상세 거래 내역")
show_cols = ["주문ID", "주문일자", "카테고리", "제품명", "지역",
             "판매채널", "수량", "단가", "할인율", "최종매출"]
st.dataframe(
    df[show_cols].sort_values("주문일자", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "단가": st.column_config.NumberColumn(format="%,d원"),
        "최종매출": st.column_config.NumberColumn(format="%,d원"),
        "주문일자": st.column_config.DateColumn(format="YYYY-MM-DD"),
    },
)

csv = df[show_cols].to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ 현재 필터 결과 CSV 다운로드",
    data=csv,
    file_name=f"sales_filtered_{start_d}_{end_d}.csv",
    mime="text/csv",
)

st.caption("💡 샘플 데이터 기반 대시보드입니다. 실제 데이터로 교체하려면 `data_generator.py` 대신 CSV/DB를 로드하도록 `load_data()`를 수정하세요.")
