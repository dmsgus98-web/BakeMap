import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="BakeMap - 베이커리 상권 분석", layout="wide")

# 2. Mock Data (기획안의 '서울시 제과점 인허가 정보' 구조 반영) [cite: 31, 32]
@st.cache_data
def load_mock_data():
    districts = ['마포구', '서초구', '강남구', '성동구']
    data = []
    for dist in districts:
        for year in range(2020, 2026):
            data.append({
                "자치구": dist,
                "연도": year,
                "개업수": np.random.randint(5, 20),
                "폐업수": np.random.randint(3, 15),
                "현재매장수": np.random.randint(50, 150),
                "면적_km2": 15.0  # 가상 면적
            })
    return pd.DataFrame(data)

df = load_mock_data()

# 3. 사이드바 - 지역 선택 [cite: 55]
st.sidebar.title("📍 상권 선택")
selected_district = st.sidebar.selectbox("자치구를 선택하세요", df['자치구'].unique())

# 4. 데이터 가공 및 SRS 알고리즘 반영 [cite: 99, 103]
dist_df = df[df['자치구'] == selected_district].sort_values('연도')
latest = dist_df.iloc[-1]
prev = dist_df.iloc[-2]

# 지표 산출
closure_rate = latest['폐업수'] / (latest['개업수'] + 1) # 최근 폐업률
density = latest['현재매장수'] / latest['면적_km2']     # 밀집도
growth_rate = (latest['개업수'] - prev['개업수']) / (prev['개업수'] + 1) # 개업 증가율

# SRS 점수 계산 (Min-Max 정규화 과정은 생략하고 가중치 중심 산출)
# 실제 구현 시 서울시 전체 데이터 기준 정규화 필요 [cite: 101]
srs_score = (closure_rate * 40) + (min(density, 100) * 0.35) + (max(growth_rate, 0) * 25)
srs_score = min(round(srs_score, 1), 100)

# 5. 메인 대시보드
st.title(f"🥐 BakeMap: {selected_district} 분석 리포트")
st.markdown("---")

# 핵심 지표 카드 [cite: 59, 60]
col1, col2, col3, col4 = st.columns(4)
col1.metric("현재 매장 수", f"{latest['현재매장수']}개")
col2.metric("최근 개업", f"{latest['개업수']}건", f"{latest['개업수'] - prev['개업수']}건")
col3.metric("최근 폐업", f"{latest['폐업수']}건")

# 위험도 점수 및 등급 표시 [cite: 105]
if srs_score <= 30:
    color, label = "green", "창업 유망"
elif srs_score <= 50:
    color, label = "orange", "보통"
else:
    color, label = "red", "진입 주의"

col4.markdown(f"**창업 위험도 점수(SRS)**")
col4.subheader(f":{color}[{srs_score}점 / {label}]")

# 6. 시계열 분석 그래프 [cite: 63]
st.subheader("📈 연도별 개·폐업 추이")
fig = px.bar(dist_df, x='연도', y=['개업수', '폐업수'], 
             barmode='group',
             color_discrete_map={'개업수': '#3498db', '폐업수': '#e74c3c'})
st.plotly_chart(fig, use_container_width=True)

# 7. 분석 코멘트 [cite: 65]
st.subheader("🔍 데이터 인사이트")
if latest['폐업수'] > latest['개업수']:
    st.warning(f"현재 {selected_district}은 폐업이 개업을 초과하는 쇠퇴기 국면일 가능성이 높습니다.")
else:
    st.success(f"현재 {selected_district}은 신규 진입이 활발한 성장기 상권입니다.")

# 8. 리포트 생성 버튼 (Placeholder) [cite: 74]
if st.button("📄 분석 리포트 PDF 생성"):
    st.info("비즈니스 플랜 구독 시 이용 가능한 기능입니다.")
