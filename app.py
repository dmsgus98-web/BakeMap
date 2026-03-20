import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math, os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 스타일 설정 (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: #F8F6F2; }
    .ptitle { font-size: 28px; font-weight: 700; color: #1C1917; margin-bottom: 20px; }
    .ptitle em { color: #B8622A; font-style: normal; }
</style>
""", unsafe_allow_html=True)

# 3. 유틸리티 함수 (좌표 변환 등)
def tm_to_wgs84(x, y):
    try:
        x, y = float(x), float(y)
        # 단순화된 변환 로직 (서울 지역 근사치)
        lat = 37.5 + (y - 450000) / 111000
        lon = 127.0 + (x - 200000) / 88800
        return lat, lon
    except: return np.nan, np.nan

# 4. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    file_path = "서울시_제과점영업_인허가_정보.csv"
    if not os.path.exists(file_path):
        # 파일명이 다를 경우를 대비한 예외 처리
        st.error("CSV 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, encoding='cp949')
    # 자치구 추출
    df['자치구'] = df['지번주소'].str.extract(r'서울특별시\s+(\S+구)')
    # 날짜 처리
    df['인허가일자'] = pd.to_datetime(df['인허가일자'], errors='coerce')
    df['폐업일자'] = pd.to_datetime(df['폐업일자'], errors='coerce')
    df['개업연도'] = df['인허가일자'].dt.year
    df['폐업연도'] = df['폐업일자'].dt.year
    df['영업상태'] = df['영업상태명'].apply(lambda x: '영업' if x == '영업/정상' else '폐업')
    return df

raw_df = load_data()

# 5. 구별 데이터 요약 계산
@st.cache_data
def get_summary(df):
    if df.empty: return []
    summary = []
    gu_list = df['자치구'].dropna().unique()
    
    for gu in gu_list:
        sub = df[df['자치구'] == gu]
        active_count = len(sub[sub['영업상태'] == '영업'])
        closed_count = len(sub[sub['영업상태'] == '폐업'])
        
        # 최근 데이터(2024~2026) 기반 위험도 계산
        recent_open = len(sub[sub['개업연도'] >= 2024])
        recent_close = len(sub[sub['폐업연도'] >= 2024])
        
        # SRS 점수 산출 로직 (밀집도와 최근 폐업률 반영)
        density_score = min(active_count / 100, 1) * 40  # 매장 100개 기준
        closure_score = (recent_close / max(recent_open, 1)) * 40
        srs = round(min(density_score + closure_score + 10, 100), 1)
        
        # 등급 판정 (현실화된 기준)
        if srs >= 75: grade, cls = "고위험", "danger"
        elif srs >= 55: grade, cls = "주의", "caution"
        elif srs >= 35: grade, cls = "보통", "ok"
        else: grade, cls = "유망", "safe"
        
        summary.append({
            'region': gu, 'srs': srs, 'grade': grade, 'cls': cls,
            'active': active_count, 'closed': closed_count
        })
    return summary

regions_summary = get_summary(raw_df)

# 6. 사이드바 구성
with st.sidebar:
    st.title("🥐 BakeMap 필터")
    if regions_summary:
        target_gu = st.selectbox("분석 구 선택", [r['region'] for r in regions_summary])
        risk_filter = st.slider("SRS 위험도 범위", 0, 100, (0, 100))
        min_shops = st.number_input("최소 매장 수", 0, 1000, 10)
    else:
        st.stop()

# 7. 필터링 로직 (KeyError 방지)
filtered_data = [
    r for r in regions_summary 
    if risk_filter[0] <= r['srs'] <= risk_filter[1] and r['active'] >= min_shops
]

# 8. 메
