import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math, os

# 1. 페이지 설정
st.set_page_config(page_title="BakeMap", page_icon="🥐", layout="wide")

# 2. 스타일 (생략 가능하나 가독성을 위해 최소한 유지)
st.markdown("""<style>.ptitle { font-size: 26px; font-weight: 700; }</style>""", unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data
def load_data():
    file_path = "서울시_제과점영업_인허가_정보.csv"
    if not os.path.exists(file_path): return pd.DataFrame()
    df = pd.read_csv(file_path, encoding='cp949')
    df['자치구'] = df['지번주소'].str.extract(r'서울특별시\s+(\S+구)')
    df['인허가일자'] = pd.to_datetime(df['인허가일자'], errors='coerce')
    df['폐업일자'] = pd.to_datetime(df['폐업일자'], errors='coerce')
    df['개업연도'] = df['인허가일자'].dt.year
    df['폐업연도'] = df['폐업일자'].dt.year
    df['영업여부'] = df['영업상태명'] == '영업/정상'
    return df

raw_df = load_data()

# 4. SRS 지수 완화 로직 (핵심 수정 구간)
@st.cache_data
def get_soft_summary(df):
    if df.empty: return []
    summary = []
    gu_list = df['자치구'].dropna().unique()
    
    for gu in gu_list:
        sub = df[df['자치구'] == gu]
        active = int(sub['영업여부'].sum())
        
        # 최근 3년(2024~2026) 데이터 기반 분석
        r_open = len(sub[sub['개업연도'] >= 2024])
        r_close = len(sub[sub['폐업연도'] >= 2024])
        
        # [수정된 SRS 공식]
        # 1. 밀집도(30%): 서울 평균을 고려하여 150개 이상일 때만 만점 처리
        density_score = min(active / 150, 1) * 30 
        # 2. 최근 폐업비율(40%): 개업 대비 폐업이 1.5배 넘을 때만 큰 감점
        closure_ratio = r_close / max(r_open, 1)
        closure_score = min(closure_ratio / 1.5, 1) * 40
        # 3. 순증감 페널티(30%): 폐업이 개업보다 많을 때만 점수 추가
        net_loss = max(0, r_close - r_open)
        loss_score = min(net_loss / 10, 1) * 30
        
        # 최종 점수 산출 및 보정 (기본 점수 하향)
        srs = round(density_score + closure_score + loss_score, 1)
        
        # [등급 커트라인 완화]
        if srs >= 75: grade, cls = "고위험", "danger"
        elif srs >= 55: grade, cls = "주의", "caution"
        elif srs >= 35: grade, cls = "보통", "ok"
        else: grade, cls = "유망", "safe"
        
        summary.append({
            'region': gu, 'srs': srs, 'grade': grade, 'cls': cls,
            'active': active, 'closed': int((~sub['영업여부']).sum())
        })
    return summary

regions = get_soft_summary(raw_df)

# 5. UI 구성
with st.sidebar:
    st.title("🥐 BakeMap")
    if regions:
        sel_gu = st.selectbox("지역 선택", [r['region'] for r in regions])
        r_range = st.slider("SRS 범위", 0, 100, (0, 100))
    else: st.stop()

# 필터링 및 에러 방지
filtered = [r for r in regions if r_range[0] <= r['srs'] <= r_range[1]]
info = next(r for r in regions if r['region'] == sel_gu)

st.markdown(f'<div class="ptitle">{sel_gu} 상권 리포트</div>', unsafe_allow_html=True)

# 지표 출력
c1, c2, c3 = st.columns(3)
c1.metric("상권위험도(SRS)", f"{info['srs']}점", info['grade'])
c2.metric("영업중 매장", f"{info['active']}개")
c3.metric("누적 폐업", f"{info['closed']}개")

# 비교 차트
st.subheader("📊 지역별 비교 (완화된 기준)")
if filtered:
    df_f = pd.DataFrame(filtered).sort_values("srs")
    colors = {"danger": "#EF4444", "caution": "#F97316", "ok": "#EAB308", "safe": "#22C55E"}
    fig = go.Figure(go.Bar(
        x=df_f['srs'], y=df_f['region'], orientation='h',
        marker_color=[colors[c] for c in df_f['cls']],
        text=df_f['srs'], textposition='outside'
    ))
    fig.update_layout(height=max(400, len(df_f)*20), margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("조건에 맞는 데이터가 없습니다.")
