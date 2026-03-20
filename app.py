import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# [설정] 페이지 레이아웃 및 테마
st.set_page_config(page_title="BakeMap | 분석가용 대시보드", layout="wide")

# [디자인] 세련된 스타일을 위한 CSS 주입
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e1e4e8; padding: 15px; border-radius: 12px; }
    .stTable { border-radius: 10px; overflow: hidden; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# [데이터] 기획안 3.1 & 7.2 지표 반영 [cite: 32, 99]
@st.cache_data
def get_refined_data():
    data = {
        '행정동': ['연남동', '성수동', '한남동', '방배동', '망원동'],
        'SRS': [71.5, 32.1, 45.8, 55.2, 28.4], # 창업 위험도 점수 [cite: 95]
        '현재매장': [20, 35, 18, 22, 25], # [cite: 60]
        '개업_1년': [4, 12, 5, 3, 8], # [cite: 60]
        '폐업_1년': [6, 2, 4, 5, 1], # [cite: 60]
        'lat': [37.561, 37.544, 37.535, 37.483, 37.556],
        'lon': [126.924, 127.056, 127.001, 126.991, 126.901]
    }
    df = pd.DataFrame(data)
    # 기획안 7.4 해석 기준 적용 [cite: 105]
    conditions = [
        (df['SRS'] >= 71), (df['SRS'] >= 51), (df['SRS'] >= 31), (df['SRS'] < 31)
    ]
    choices = ['🔴 고위험', '🟠 진입주의', '🟡 보통', '🟢 유망']
    df['상태'] = np.select(conditions, choices, default='미분류')
    return df

df = get_refined_data()

# [Header]
st.title("🥐 BakeMap: 입지 분석 대시보드")
st.info("서울시 제과점 인허가 공공데이터 기반 창업 의사결정 지원 서비스 [cite: 7, 12]")

# [Layout] 상단: 지도와 핵심 지표
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📍 지역별 밀집도 및 위험도") [cite: 48, 54]
    m = folium.Map(location=[37.54, 126.98], zoom_start=12, tiles="CartoDB positron")
    
    for _, row in df.iterrows():
        # SRS 점수에 따른 색상 매핑 [cite: 105]
        marker_color = 'red' if row['SRS'] >= 71 else ('orange' if row['SRS'] >= 51 else 'green')
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['현재매장'] * 0.4 + 5,
            color=marker_color,
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{row['행정동']}: {row['SRS']}점",
            popup=f"현재 매장수: {row['현재매장']}개"
        ).add_to(m)
    
    st_folium(m, width="100%", height=450, key="bakemap_main")

with col_right:
    st.subheader("📊 상권 요약 지표") [cite: 58]
    target_dong = st.selectbox("상세 분석 지역", df['행정동'])
    res = df[df['행정동'] == target_dong].iloc[0]
    
    # 지표 카드 디자인 [cite: 59, 60]
    st.metric(label="창업 위험도(SRS)", value=f"{res['SRS']}점", delta=res['상태'], delta_color="inverse")
    st.write(f"**현재 운영 매장:** {res['현재매장']}개")
    
    # 미니 차트: 최근 1년 개/폐업 추이 [cite: 63]
    fig = px.bar(
        x=['개업', '폐업'], 
        y=[res['개업_1년'], res['폐업_1년']],
        color=['개업', '폐업'],
        color_discrete_map={'개업': '#3498db', '폐업': '#e74c3c'},
        height=250
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# [Bottom] 데이터 상세 테이블 (가독성 강조) [cite: 48, 113]
st.markdown("---")
st.subheader("📋 지역별 분석 데이터 상세")

# 데이터프레임 스타일링
def highlight_risk(s):
    return ['background-color: #ffe9e9' if v == '🔴 고위험' else '' for v in s]

styled_table = df[['행정동', 'SRS', '상태', '현재매장', '개업_1년', '폐업_1년']].style\
    .apply(highlight_risk, subset=['상태'])\
    .format({'SRS': '{:.1f}'})\
    .set_properties(**{'text-align': 'center'})

st.table(styled_table)

# [Footer] 리포트 생성 [cite: 74, 117]
if st.button("📄 선택 지역 PDF 분석 리포트 생성"):
    st.toast(f"{target_dong} 리포트를 생성 중입니다...", icon='⏳')
