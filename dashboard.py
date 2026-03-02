import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt

# 한글 폰트 설정 (배포 환경 대응)
try:
    import koreanize_matplotlib
except ImportError:
    plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 로컬용
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title="NemoStore 부동산 대시보드", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_data():
    conn = sqlite3.connect("nemostore.db")
    df = pd.read_sql_query("SELECT * FROM stores", conn)
    conn.close()
    
    # 데이터 가공 (JSON 값 / 10 = 만원 단위 매핑 반영)
    df['deposit_man'] = df['deposit'] / 10
    df['monthlyRent_man'] = df['monthlyRent'] / 10
    df['premium_man'] = df['premium'] / 10
    
    # 단위 환산 텍스트 생성 (예: 3,000만)
    def format_money(val):
        if val >= 10000:
            return f"{val/10000:,.1f}억"
        return f"{val:,.0f}만"
        
    df['deposit_txt'] = df['deposit_man'].apply(format_money)
    df['monthlyRent_txt'] = df['monthlyRent_man'].apply(format_money)
    
    return df

# 메인 앱 로직
def main():
    st.title("🏠 NemoStore 부동산 매물 대시보드")
    st.markdown("수집된 **200개**의 매물 데이터를 분석하고 시각화합니다.")
    
    df = load_data()
    
    # 사이드바 필터
    st.sidebar.header("🔍 필터 설정")
    
    # 업종 필터
    business_types = df['businessMiddleCodeName'].unique()
    selected_bus = st.sidebar.multiselect("현 업종 선택", business_types, default=business_types)
    
    # 층수 필터
    min_floor, max_floor = int(df['floor'].min()), int(df['floor'].max())
    selected_floor = st.sidebar.slider("층수 범위", min_floor, max_floor, (min_floor, max_floor))
    
    # 데이터 필터링
    mask = (df['businessMiddleCodeName'].isin(selected_bus)) & (df['floor'].between(selected_floor[0], selected_floor[1]))
    filtered_df = df[mask]
    
    # 주요 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 매물 수", f"{len(filtered_df)}개")
    with col2:
        avg_deposit = filtered_df['deposit_man'].mean()
        st.metric("평균 보증금", f"{avg_deposit/10000:,.1f}억" if avg_deposit >= 10000 else f"{avg_deposit:,.0f}만")
    with col3:
        avg_rent = filtered_df['monthlyRent_man'].mean()
        st.metric("평균 월세", f"{avg_rent:,.0f}만")
    with col4:
        avg_premium = filtered_df['premium_man'].mean()
        st.metric("평균 권리금", f"{avg_premium:,.0f}만")
        
    st.divider()
    
    # 차트 영역
    c1, c2 = st.columns(2)
    
    with c1:
        # 보증금 vs 월세 산점도
        st.subheader("💰 보증금 vs 월세 분포")
        fig_scatter = px.scatter(
            filtered_df, x="deposit_man", y="monthlyRent_man", 
            size="size", color="businessMiddleCodeName",
            hover_name="title", labels={"deposit_man": "보증금 (만원)", "monthlyRent_man": "월세 (만원)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with c2:
        # 업종별 분포 파이 차트
        st.subheader("📊 업종별 비중")
        bus_counts = filtered_df['businessMiddleCodeName'].value_counts().reset_index()
        fig_pie = px.pie(bus_counts, values='count', names='businessMiddleCodeName', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.divider()
    
    # 두 번째 차트 영역
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🏢 층별 매물 분포")
        floor_counts = filtered_df['floor'].value_counts().sort_index()
        st.bar_chart(floor_counts)
        
    with c4:
        st.subheader("📐 전용면적 분포 (㎡)")
        fig_hist = px.histogram(filtered_df, x="size", nbins=20, labels={"size": "전용면적 (㎡)"})
        st.plotly_chart(fig_hist, use_container_width=True)
        
    st.divider()
    
    # 상세 데이터 테이블
    st.subheader("📑 상세 데이터")
    display_cols = ['title', 'businessMiddleCodeName', 'floor', 'size', 'deposit_txt', 'monthlyRent_txt', 'nearSubwayStation']
    st.dataframe(filtered_df[display_cols], use_container_width=True)

if __name__ == "__main__":
    main()

st.title("네모스토어 매출 분석")
st.write("2026년 1분기 데이터 시각화")