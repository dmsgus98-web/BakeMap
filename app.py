import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# 페이지 설정 (Wide 모드 및 테마 설정)
st.set_page_config(page_title="BakeMap | 상권 분석 솔루션", layout="wide")

# 커스텀 CSS로 디자인 세련되게 조정
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.stButton > button:first-child { background-color: #FF4B4B; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 1. Mock Data 생성 (기획안 기반) [cite: 31, 32]
@st.cache_data
def load_data():
    data = {
        '행정동': ['연남동', '성수동', '한남동', '방배동', '망원동'],
        'SRS_점수': [71, 32, 45, 55, 28],
        '영업매장': [20, 35, 18, 22, 25],
        '최근개업': [4, 12, 5, 3, 8],
        '최근폐업': [6, 2, 4, 5, 1],
        'lat': [37.561, 37.544, 37.535, 37.483, 37.556],
        'lon': [126.924, 127.056, 127.001, 126.991, 126.901]
    }
    df = pd.DataFrame(data)
    # 위험도 등급 산출 [cite: 105]
    df['등급'] = df['SRS_점수'].apply(lambda x: '고위험' if x >= 71 else ('진입주의' if x >= 51 else '보통' if x >= 31 else '유망'))
    return df

df = load_data()

# 헤더 섹션
st.title("🥐 BakeMap: 데이터 기반 상권 분석")
st.markdown(f"**서울시 제과점 인허가 공공데이터**를 기반으로 실시간 창업 위험도를 산출합니다. [cite: 7, 12]")

# 2. 메인 대시보드 레이아웃
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("📍 지역별 창업 위험도 지도")
    # 지도 생성 (CartoDB Positron 타일로 세련되게 표현)
    m = folium.Map(location=[37.54, 127.00], zoom_start=12, tiles="cartodbpositron")
    
    for _, row in df.iterrows():
        # 등급별 색상 [cite: 105]
        color = '#RRGGBB'
        if row['SRS_점수'] >= 71: color = '#e74c3c' # Red
        elif row['SRS_점수'] >= 51: color = '#f39c12' # Orange
        elif row['SRS_점수'] >= 31: color = '#f1c40f' # Yellow
        else: color = '#2ecc71' # Green
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['영업매장'] * 0.5 + 5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            tooltip=f"<b>{row['행정동']}</b><br>SRS: {row['SRS_점수']}점 ({row['등급']})",
            popup=f"영업 중: {row['영업매장']}개 / 최근 폐업: {row['최근폐업']}건"
        ).add_to(m)
    
    st_folium(m, width="100%", height=500)

with col_stats:
    st.subheader("📊 상권 요약 지표") [cite: 58]
    selected_dong = st.selectbox("상세 분석 동 선택", df['행정동'])
    row = df[df['행정동'] == selected_dong].iloc[0]
    
    # 메트릭 카드 [cite: 60]
    st.metric("창업 위험도(SRS)", f"{row['SRS_점수']}점", row['등급'], delta_color="inverse")
    st.metric("현재 영업 매장", f"{row['영업매장']}개")
    st.write(f"**최근 1년 동향**")
    st.write(f"- 개업: {row['최근개업']}건 / 폐업: {row['최근폐업']}건")
    
    # 미니 차트 (개폐업 비중)
    fig = px.pie(values=[row['최근개업'], row['최근폐업']], names=['개업', '폐업'], 
                 color_discrete_sequence=['#3498db', '#e74c3c'], hole=0.4)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=200, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 3. 하단 데이터 테이블 (가독성 강조)
st.markdown("---")
st.subheader("📝 지역별 상세 데이터 리포트") [cite: 48, 73]

# Pandas Styling을 이용한 가독성 향상
def style_srs(val):
    color = '#2ecc71' if val < 31 else ('#f1c40f' if val < 51 else '#e74c3c')
    return f'color: {color}; font-weight: bold'

styled_df = df[['행정동', 'SRS_점수', '등급', '영업매장', '최근개업', '최근폐업']].style\
    .applymap(style_srs, subset=['SRS_점수'])\
    .background_gradient(cmap='YlOrRd', subset=['최근폐업'])\
    .format({'SRS_점수': '{:.1f}점'})

st.table(styled_df) # 혹은 st.dataframe(styled_df, use_container_width=True)

# PDF 리포트 생성 버튼 [cite: 75, 113]
if st.sidebar.button("📄 선택 지역 PDF 리포트 출력"):
    st.sidebar.success(f"{selected_dong} 상권 분석 리포트 생성을 시작합니다.")
