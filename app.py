import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import math, os

st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  STYLES (기존 스타일 유지)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Lora:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1C1917; }
.stApp { background: #F8F6F2; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E7E4DF; }
.wm-title { font-family: 'Lora', serif; font-size: 20px; color: #B8622A; }
.ptitle { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; }
.ptitle em { color: #B8622A; font-style: normal; }
.kcard { background: #FFFFFF; border: 1px solid #E7E4DF; border-radius: 12px; padding: 15px; }
.bdg { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.bdg-safe { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.bdg-ok { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.bdg-caution { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }
.bdg-danger { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.insight { border-radius: 10px; padding: 12px; font-size: 13px; margin-bottom: 10px; }
.ins-good { background: #F0FDF4; border-left: 3px solid #22C55E; color: #14532D; }
.ins-warn { background: #FFF7ED; border-left: 3px solid #F97316; color: #7C2D12; }
.cmp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cmp-table th { background: #F5F2EE; padding: 10px; text-align: left; border-bottom: 2px solid #E7E4DF; }
.cmp-table td { padding: 10px; border-bottom: 1px solid #F0EDE8; }
</style>
""", unsafe_allow_html=True)

# Plotly 기본 설정
BASE = dict(font_family="Noto Sans KR", font_color="#1C1917", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
AX = dict(gridcolor="#EDE9E4", showline=False)
def lay(**kw): return {**BASE, **kw}

CMAP = {"safe": "#22C55E", "ok": "#EAB308", "caution": "#B8622A", "danger": "#EF4444"}
BDGCLS = {"safe": "bdg-safe", "ok": "bdg-ok", "caution": "bdg-caution", "danger": "bdg-danger"}
GLABEL = {"safe": "유망", "ok": "보통", "caution": "주의", "danger": "고위험"}

# TM 좌표 변환 함수 (기존 유지)
def tm_to_wgs84(x, y):
    try:
        a=6378137.0; f=1/298.257222101; b=a*(1-f); e2=1-(b/a)**2
        k0=1.0; lat0=math.radians(38); lon0=math.radians(127)
        FE=200000.0; FN=500000.0
        x_=float(x)-FE; y_=float(y)-FN
        M0=a*((1-e2/4-3*e2**2/64)*lat0-(3*e2/8+3*e2**2/32)*math.sin(2*lat0)+(15*e2**2/256)*math.sin(4*lat0))
        M=M0+y_/k0; mu=M/(a*(1-e2/4-3*e2**2/64))
        e1=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
        phi1=mu+(3*e1/2-27*e1**3/32)*math.sin(2*mu)+(21*e1**2/16)*math.sin(4*mu)
        N1=a/math.sqrt(1-e2*math.sin(phi1)**2); T1=math.tan(phi1)**2
        C1=e2*math.cos(phi1)**2/(1-e2); R1=a*(1-e2)/(1-e2*math.sin(phi1)**2)**1.5
        D=x_/(N1*k0)
        lat=phi1-(N1*math.tan(phi1)/R1)*(D**2/2-(5+3*T1+10*C1-4*C1**2-9*e2)*D**4/24)
        lon=lon0+(D-(1+2*T1+C1)*D**3/6)/math.cos(phi1)
        return round(math.degrees(lat),5), round(math.degrees(lon),5)
    except: return np.nan, np.nan

# ══════════════════════════════════════════════════════════════
#  DATA LOAD
# ══════════════════════════════════════════════════════════════
DATA_PATH = "서울시_제과점영업_인허가_정보.csv"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"파일을 찾을 수 없습니다: {DATA_PATH}")
        st.stop()
    
    df = pd.read_csv(DATA_PATH, encoding='cp949')
    df['자치구'] = df['지번주소'].str.extract(r'서울특별시\s+(\S+구)')
    df['인허가일자'] = pd.to_datetime(df['인허가일자'], errors='coerce')
    df['폐업일자'] = pd.to_datetime(df['폐업일자'], errors='coerce')
    df['개업연도'] = df['인허가일자'].dt.year
    df['폐업연도'] = df['폐업일자'].dt.year
    df['영업여부'] = df['영업상태명'] == '영업/정상'
    
    # 좌표 변환
    has_xy = df['좌표정보(X)'].notna() & df['좌표정보(Y)'].notna()
    df.loc[has_xy, ['lat', 'lng']] = df[has_xy].apply(lambda r: tm_to_wgs84(r['좌표정보(X)'], r['좌표정보(Y)']), axis=1, result_type='expand')
    return df

raw_df = load_data()

@st.cache_data
def get_regions_summary(_df):
    gu_list = _df['자치구'].dropna().unique()
    rows = []
    # 최신 데이터 반영을 위해 연도 범위 확장 (2026년 포함)
    target_years = range(2015, 2027) 
    
    for gu in gu_list:
        sub = _df[_df['자치구'] == gu]
        active = int(sub['영업여부'].sum())
        closed = int((~sub['영업여부']).sum())
        
        # 최근 3년 데이터 (2024~2026)
        recent_open = int(sub['개업연도'].between(2024, 2026).sum())
        recent_close = int(sub['폐업연도'].between(2024, 2026).sum())
        closure_rate = recent_close / max(recent_open, 1)
        
        # SRS 점수 계산 (기준 완화)
        # 밀집도 점수 비중을 낮추고 성장을 더 반영함
        density = active / 25.0 # 평균 구 면적 기준
        srs = (closure_rate * 35) + (min(density/30, 1) * 35) + (max(0, (recent_close-recent_open)/10) * 30)
        srs = round(min(max(srs * 10, 0), 100), 1)
        
        # 등급 기준 조정 (75점 이상을 고위험으로)
        if srs >= 75: grade, cls = "고위험", "danger"
        elif srs >= 55: grade, cls = "주의", "caution"
        elif srs >= 35: grade, cls = "보통", "ok"
        else: grade, cls = "유망", "safe"
        
        trend = []
        for y in target_years:
            trend.append({'year': y, 'open': int((sub['개업연도']==y).sum()), 'close': int((sub['폐업연도']==y).sum())})
            
        rows.append({
            'region': gu, 'srs': srs, 'grade': grade, 'cls': cls,
            'active': active, 'closed': closed, 'survival': active/(active+closed) if (active+closed)>0 else 0,
            'lat': sub['lat'].median(), 'lng': sub['lng'].median(), 'trend': trend
        })
    return rows

regions = get_regions_summary(raw_df)

# ══════════════════════════════════════════════════════════════
#  SIDEBAR & FILTER
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="wm-title">🥐 BakeMap</div>', unsafe_allow_html=True)
    sel_gu = st.selectbox("분석 지역", [r['region'] for r in regions])
    risk_range = st.slider("SRS 위험도 범위", 0, 100, (0, 100))
    min_active = st.slider("최소 영업 매장 수", 0, 500, 0)

# 필터링 적용 (에러 방지 핵심)
filtered_regions = [r for r in regions if risk_range[0] <= r['srs'] <= risk_range[1] and r['active'] >= min_active]
info = next(r for r in regions if r['region'] == sel_gu)

# ══════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════
st.markdown(f
