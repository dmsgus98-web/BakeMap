import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# 1. 페이지 기본 설정
st.set_page_config(page_title="BakeMap - 베이커리 상권 분석", layout="wide")

# 2. 데이터 준비 (기획안의 SRS 점수 로직 반영)
@st.cache_data
def load_data():
    data = {
        '지역': ['연남동', '성수동', '한남동', '방배동', '망원동'],
        '위험점수': [71.5, 32.1, 45.8, 55.2, 28.4],
        '매장수': [20, 35, 18, 22, 25],
        '최근개업': [4, 12, 5, 3, 8],
        '최근폐업': [6, 2, 4, 5, 1],
        '위도': [37.561, 37.544, 37.535, 37.483, 37.556],
        '경도': [126.924, 127.056, 127.001, 126.991, 126.901]
    }
    df = pd.DataFrame(data)
    
    # 위험도 등급 분류
    def get_status(score):
        if score >= 71: return '🔴 고위험'
        if score >= 51: return '🟠 주의'
        if score >= 31: return '🟡 보통'
        return '🟢 유망'
    
    df['상태'] = df['위험점수'].apply(get_status)
    return df

# 데이터 불러오기
main_df = load_data()

# 3. 화면 UI 디자인
st.title("🥐 BakeMap: 베이커리 창업 입지 분석")
st.markdown("공공데이터 기반 **창업 위험도 점수(SRS)**를 확인하세요.")
st.write("---")

# 상단 레이아웃: 왼쪽(지도), 오른쪽(상세정보)
col1, col2 = st.columns([1.5, 1], gap="medium")

with col1:
    st.subheader("📍 지역별 상권 지도")
    # 지도 중심 설정
    m = folium.Map(location=[37.54, 126.98], zoom_start=12, tiles="cartodbpositron")
    
    # 지도에 마커 찍기
    for _, row in main_df.iterrows():
        # 등급별 색상
        m_color = 'red' if '고위험' in row['상태'] else ('orange' if '주의' in row['상태'] else 'green')
        
        folium.CircleMarker(
            location=[row['위도'], row['경도']],
            radius=row['매장수'] * 0.5 + 5,
            color=m_color,
            fill=True,
            fill_opacity=0.6,
            tooltip=f"{row['지역']}: {row['위험점수']}점",
        ).add_to(m)
    
    st_folium(m, width="100%", height=450, key="map")

with col2:
    st.subheader("📊 지역별 상세 지표")
    # 선택 상자
    selected = st.selectbox("분석할 동네를 선택하세요", main_df['지역'])
    info = main_df[main_df['지역'] == selected].iloc[0]
    
    # 주요 지표 표시
    st.metric(label="창업 위험도 점수", value=f"{info['위험점수']}점", delta=info['상태'], delta_color="inverse")
    
    # 개업/폐업 비교 차트
    chart_data = pd.DataFrame({
        '구분': ['최근 개업', '최근 폐업'],
        '건수': [info['최근개업'], info['최근폐업']]
    })
    fig = px.bar(chart_data, x='구분', y='건수', color='구분', 
                 color_discrete_map={'최근 개업': '#3498db', '최근 폐업': '#e74c3c'})
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

# 4. 하단 데이터 표 (가독성 강조)
st.write("---")
st.subheader("📋 전체 지역 요약 리포트")

# 표 디자인 수정
def highlight_row(val):
    if '고위험' in str(val): return 'background-color: #ffcccc'
    if '유망' in str(val): return 'background-color: #e6ffed'
    return ''

display_df = main_df[['지역', '상태', '위험점수', '매장수', '최근개업', '최근폐업']]
st.dataframe(display_df.style.applymap(highlight_row, subset=['상태']), use_container_width=True)

# 5. 리포트 다운로드 버튼 (기능 예시)
if st.button("📄 분석 결과 PDF로 받기"):
    st.success(f"{selected} 지역 분석 리포트 생성을 시작합니다!")
