import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import math, os

# 1. 페이지 설정
st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 스타일 (기존의 세련된 디자인 유지)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Lora:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1C1917; }
.stApp { background: #F8F6F2; }
.ptitle { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; }
.ptitle em { color: #B8622A; font-style: normal; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 및 전처리
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

# 4. SRS 지수 완화 계산 로직 (여기가 핵심입니다)
@st.cache_data
def get_regions_summary(df):
    if df.empty: return []
    summary = []
    gu_list = df['자치구'].dropna().unique()
    
    for gu in gu_list:
        sub = df[df['자치구'] == gu]
        active = int(sub['영업여부'].sum())
        closed = int((~sub['영업여부']).sum())
        
        # 최근 3년(2024~2026) 데이터 기반 분석
        r_open = len(sub[sub['개업연도'] >= 2024])
        r_close = len(sub[sub['폐업연도'] >= 2024])
        
        # [수정된 SRS 공식 - 훨씬 너그럽게]
        # 1. 밀집도(30%): 기존 100개 기준에서 180개 기준으로 완화 (180개는 되어야 과열로 판단)
        density_score = min(active / 180, 1) * 30 
        
        # 2. 최근 폐업비율(40%): 폐업이 개업보다 2배 많을 때만 최대점수 (기존 1.5배에서 완화)
        closure_ratio = r_close / max(r_open, 1)
        closure_score = min(closure_ratio / 2.0, 1) * 40
        
        # 3. 순증감 페널티(30%): 폐업이 눈에 띄게 많을 때만 점수 추가
        net_loss_score = min(max(0, r_close - r_open) / 15, 1) * 30
        
        # 최종 점수 산출
        srs = round(density_score + closure_score + net_loss_score, 1)
        
        # [등급 기준도 더 상향 조정]
        if srs >= 75: grade, cls = "고위험", "danger"   # 75점은 넘어야 위험
        elif srs >= 50: grade, cls = "주의", "caution" # 50~74점은 주의
        elif srs >= 30: grade, cls = "보통", "ok"      # 30~49점은 보통
        else: grade, cls = "유망", "safe"              # 30점 미만은 유망
        
        summary.append({
            'region': gu, 'srs': srs, 'grade': grade, 'cls': cls,
            'active': active, 'closed': closed,
            'survival': active/(active+closed) if (active+closed)>0 else 0
        })
    return summary

regions = get_regions_summary(raw_df)

# 5. 메인 UI (디자인 유지)
with st.sidebar:
    st.title("🥐 BakeMap")
    if regions:
        sel_gu = st.selectbox("분석 지역", [r['region'] for r in regions])
        risk_range = st.slider("SRS 위험도 범위", 0, 100, (0, 100))
        min_active = st.number_input("최소 매장 수", 0, 500, 10)
    else:
        st.error("데이터를 불러올 수 없습니다.")
        st.stop()

# 필터링 및 정보 추출
filtered_regions = [r for r in regions if risk_range[0] <= r['srs'] <= risk_range[1] and r['active'] >= min_active]
info = next(r for r in regions if r['region'] == sel_gu)

st.markdown(f'<div class="ptitle">{sel_gu} <em>베이커리 상권 분석</em></div>', unsafe_allow_html=True)

# 지표 카드
c1, c2, c3, c4 = st.columns(4)
c1.metric("상권위험지수(SRS)", f"{info['srs']}점", info['grade'])
c2.metric("현재 영업중", f"{info['active']}개")
c3.metric("누적 폐업", f"{info['closed']}개")
c4.metric("생존율", f"{info['survival']*100:.1f}%")

# 차트 시각화 (KeyError 방어 포함)
st.subheader("📊 지역별 비교 (완화된 기준 적용)")
if filtered_regions:
    df_f = pd.DataFrame(filtered_regions).sort_values("srs")
    colors = {"danger": "#EF4444", "caution": "#B8622A", "ok": "#EAB308", "safe": "#22C55E"}
    
    fig = go.Figure(go.Bar(
        x=df_f['srs'], y=df_f['region'], orientation='h',
        marker_color=[colors[r] for r in df_f['cls']],
        text=df_f['srs'], textposition='outside',
        textfont=dict(size=12, color="#1C1917")
    ))
    fig.update_layout(height=max(400, len(df_f)*25), margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("선택한 조건에 맞는 지역이 없습니다. 필터를 조절해 보세요.")

# 트렌드 분석 (2026년 포함)
st.subheader("📈 연도별 개/폐업 추이")
gu_df = raw_df[raw_df['자치구'] == sel_gu]
trend_open = gu_df.groupby('개업연도').size().reindex(range(2015, 2027), fill_value=0)
trend_close = gu_df.groupby('폐업연도').size().reindex(range(2015, 2027), fill_value=0)

fig_t = go.Figure()
fig_t.add_trace(go.Scatter(x=list(trend_open.index), y=list(trend_open.values), name="신규 개업", line=dict(color="#3B82F6", width=3)))
fig_t.add_trace(go.Scatter(x=list(trend_close.index), y=list(trend_close.values), name="폐업 발생", line=dict(color="#EF4444", width=3)))
fig_t.update_layout(xaxis_title="연도", yaxis_title="매장 수", height=350)
st.plotly_chart(fig_t, use_container_width=True)
