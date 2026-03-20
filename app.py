import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# [1] 페이지 설정 (최상단 고정)
st.set_page_config(page_title="BakeMap Professional", layout="wide")

# [2] 스타일 시트 (세련된 UI)
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { border: 1px solid #dee2e6; padding: 20px; border-radius: 15px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .css-1r6slb0 { border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# [3] 데이터 로딩 함수 (에러 방지를 위해 최상단에서 실행)
@st.cache_data
def load_bakemap_data():
    # 기획안 7.2 및 7.4 지표 데이터셋 [cite: 98, 105]
    data = {
        '행정동': ['연남동', '성수동', '한남동', '방배동', '망원동'],
        'SRS': [71.5, 32.1, 45.8, 55.2, 28.4],
        '현재매장': [20, 35, 18, 22, 25],
        '개업_1년': [4, 12, 5, 3, 8],
        '폐업_1년': [6, 2, 4, 5, 1],
        'lat': [37.561, 37.544, 37.535, 37.483, 37.556],
        'lon': [126.924, 127.056, 127.001, 126.991, 126.901]
    }
    df_raw = pd.DataFrame(data)
    
    # 상태 분류 로직 [cite: 105]
    def get_status(score):
        if score >= 71: return '🔴 고위험'
        if score >= 51: return '🟠 진입주의'
        if score >= 31: return '🟡 보통'
        return '🟢 유망'
    
    df_raw['상태'] = df_raw['SRS'].apply(get_status)
    return df_raw

# 변수 정의 (에러 발생 원천 차단)
df = load_bakemap_data()

# [4] 메인 타이틀
st.title("🥐 BakeMap Professional")
st.caption("Data-Driven Bakery Location Intelligence Service")
st.write("---")

# [5] 레이아웃 구성
col_left, col_right = st.columns([1.8, 1.2], gap="large")

with col_left:
    # 에러가 났던 51라인 부근: df가 위에서 정의되었으므로 안전합니다. [cite: 48, 54]
    st.subheader("📍 상권 밀집도 및 위험도 맵")
    
    # 지도 생성
    m = folium.Map(location=[37.54, 126.98], zoom_start=12, tiles="CartoDB positron")
    
    for _, row in df.iterrows():
        # 등급별 컬러 매핑 [cite: 68]
        m_color = '#e74c3c' if '고위험' in row['상태'] else ('#f39c12' if '주의' in row['상태'] else '#27ae60')
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['현재매장'] * 0.5 + 5,
            color=m_color,
            fill=True,
            fill_opacity=0.6,
            tooltip=f"<b>{row['행정동']}</b>: {row['SRS']}점",
            popup=f"현재 매장: {row['현재매장']}개"
        ).add_to(m)
    
    st_folium(m, width="100%", height=500, key="main_map")

with col_right:
    st.subheader("📊 지역별 상세 지표") [cite: 58]
    
    # 선택 박스
    selected_dong = st.selectbox("분석 대상 지역 선택", df['행정동'].unique())
    
    # 선택된 지역 데이터 추출
    analysis_data = df[df['행정동'] == selected_dong].iloc[0]
    
    # 메트릭 카드 [cite: 60, 67]
    c1, c2 = st.columns(2)
    with c1:
        st.metric("위험도 점수 (SRS)", f"{analysis_data['SRS']}점", analysis_data['상태'], delta_color="inverse")
    with c2:
        st.metric("운영 매장 수", f"{analysis_data['현재매장']}개")
    
    st.write("")
    
    # 시계열 대용 바 차트 (개업/폐업 비중) [cite: 62]
    chart_df = pd.DataFrame({
        '구분': ['최근 개업', '최근 폐업'],
        '건수': [analysis_data['개업_1년'], analysis_data['폐업_1년']]
    })
    
    fig = px.bar(chart_df, x='구분', y='건수', color='구분',
                 color_discrete_map={'최근 개업': '#3498db', '최근 폐업': '#e74c3c'},
                 text_auto=True)
    fig.update_layout(showlegend=False, height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

# [6] 하단 데이터 테이블 (가독성 1순위)
st.write("---")
st.subheader("📋 전체 지역 분석 데이터") [cite: 48]

# 테이블 가독성을 위한 스타일링
def color_status(val):
    color = '#ffebee' if '고위험' in val else ('#fff3e0' if '주의' in val else '#e8f5e9')
    return f'background-color: {color}'

# 필요한 컬럼만 추출하여 정렬
display_df = df[['행정동', '상태', 'SRS', '현재매장', '개업_1년', '폐업_1년']].sort_values(by='SRS', ascending=False)

# 세련된 테이블 출력
st.dataframe(
    display_df.style.applymap(color_status, subset=['상태']),
    use_container_width=True,
    height=250
)

# [7] 사이드바 기능 (PDF 리포트 등) [cite: 73, 75]
with st.sidebar:
    st.title("Settings")
    if st.button("📄 분석 리포트 PDF 생성"):
        st.success(f"{selected_dong} 지역 리포트를 준비 중입니다.")
    st.divider()
    st.info("BakeMap v1.0 - Data Scientist Edition")
