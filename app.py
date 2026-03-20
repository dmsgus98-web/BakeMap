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
#  STYLES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Lora:wght@600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1C1917; }
.stApp { background: #F8F6F2; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E7E4DF; }
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] { display: none !important; }
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding: 1.8rem 2rem 2rem; }

.wm { padding: 22px 16px 16px; border-bottom: 1px solid #F0EDE8; margin-bottom: 18px; }
.wm-title { font-family: 'Lora', serif; font-size: 20px; color: #B8622A; letter-spacing: -0.01em; }
.wm-sub   { font-size: 10px; font-weight: 600; color: #B0A89E; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 3px; }

.eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #B8622A; margin-bottom: 5px; }
.ptitle  { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; line-height: 1.2; margin-bottom: 4px; }
.ptitle em { color: #B8622A; font-style: normal; }
.pdesc   { font-size: 13px; color: #6B6560; margin-bottom: 20px; }

.krow { display: flex; gap: 10px; margin-bottom: 18px; flex-wrap: wrap; }
.kcard {
    flex: 1; min-width: 110px;
    background: #FFFFFF; border: 1px solid #E7E4DF;
    border-radius: 12px; padding: 15px 17px 13px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.kcard.hl { border-color: #B8622A; background: #FEF5EE; }
.klabel { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #A8A29E; margin-bottom: 7px; }
.kval   { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; line-height: 1; }
.kval.amber { color: #B8622A; }
.kdelta { font-size: 11px; font-weight: 500; color: #A8A29E; margin-top: 4px; }
.kdelta.up   { color: #16A34A; }
.kdelta.down { color: #DC2626; }

.bdg { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.bdg-safe    { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.bdg-ok      { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.bdg-caution { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }
.bdg-danger  { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }

.slabel {
    font-size: 10px; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    color: #A8A29E; margin-bottom: 12px; display: flex; align-items: center; gap: 7px;
}
.slabel::before { content:''; display:inline-block; width:3px; height:10px; background:#B8622A; border-radius:2px; }

.hr { border: none; border-top: 1px solid #E7E4DF; margin: 16px 0; }
.srow { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid #F0EDE8; font-size:13px; }
.srow:last-child { border-bottom:none; }
.skey { color: #78716C; }

.insight { border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.65; margin-bottom: 10px; }
.ins-good { background: #F0FDF4; border-left: 3px solid #22C55E; color: #14532D; }
.ins-warn { background: #FFF7ED; border-left: 3px solid #F97316; color: #7C2D12; }
.ins-neut { background: #FEFCE8; border-left: 3px solid #EAB308; color: #713F12; }

.rec-card {
    background: #FFFFFF; border: 1px solid #E7E4DF;
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: flex-start;
    transition: border-color .15s;
}
.rec-card:hover { border-color: #B8622A; background: #FEF5EE; }
.rec-name   { font-size: 15px; font-weight: 700; color: #1C1917; margin-bottom: 4px; }
.rec-reason { font-size: 12px; color: #78716C; line-height: 1.5; }

.cmp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cmp-table th { background: #F5F2EE; padding: 10px 14px; text-align: left; font-weight: 700; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: #78716C; border-bottom: 2px solid #E7E4DF; }
.cmp-table td { padding: 10px 14px; border-bottom: 1px solid #F0EDE8; color: #1C1917; font-weight: 500; }
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-table tr:hover td { background: #FAF8F5; }

.stTabs [data-baseweb="tab-list"] { background: #EDE9E4; border-radius: 10px; padding: 3px; gap: 0; border: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; padding: 7px 15px !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #78716C !important; letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] { background: #FFFFFF !important; color: #1C1917 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #FFFFFF !important; border: 1px solid #E7E4DF !important;
    border-radius: 10px !important; color: #1C1917 !important;
}

.stButton > button {
    background: #B8622A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 10px 20px !important;
    box-shadow: 0 2px 6px rgba(184,98,42,0.28) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
iframe { border-radius: 12px; }

.data-note {
    font-size: 11px; color: #A8A29E; padding: 8px 12px;
    background: #F5F2EE; border-radius: 8px; margin-bottom: 16px;
    border-left: 3px solid #D6D3CE;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PLOTLY BASE
# ══════════════════════════════════════════════════════════════
BASE = dict(
    font_family="Noto Sans KR, sans-serif", font_color="#1C1917",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=28, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font_size=11, bgcolor="rgba(0,0,0,0)"),
)
AX = dict(gridcolor="#EDE9E4", tickfont_size=11, showline=False)
def lay(**kw): return {**BASE, **kw}

CA="#B8622A"; CB="#3B82F6"; CR="#EF4444"; CG="#22C55E"; CY="#EAB308"; CM="#D6D3CE"
CMAP   = {"safe": CG, "ok": CY, "caution": CA, "danger": CR}
BDGCLS = {"safe": "bdg-safe", "ok": "bdg-ok", "caution": "bdg-caution", "danger": "bdg-danger"}
GLABEL = {"safe": "유망 ↑", "ok": "보통", "caution": "주의 ↓", "danger": "고위험 ✕"}

# ══════════════════════════════════════════════════════════════
#  COORDINATE CONVERSION (TM중부 → WGS84)
# ══════════════════════════════════════════════════════════════
def tm_to_wgs84(x, y):
    a=6378137.0; f=1/298.257222101; b=a*(1-f); e2=1-(b/a)**2
    k0=1.0; lat0=math.radians(38); lon0=math.radians(127)
    FE=200000.0; FN=500000.0
    x_=x-FE; y_=y-FN
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

# ══════════════════════════════════════════════════════════════
#  DATA LOAD & PROCESSING
# ══════════════════════════════════════════════════════════════
DATA_PATH = "서울시_제과점영업_인허가_정보.csv"

@st.cache_data(show_spinner="📊 서울시 인허가 데이터 불러오는 중...")
def load_raw():
    # Streamlit Cloud: 앱과 같은 디렉토리에 CSV 파일 위치
    path = DATA_PATH if os.path.exists(DATA_PATH) else \
           os.path.join(os.path.dirname(__file__), DATA_PATH)
    df = pd.read_csv(path, encoding='cp949')

    df['자치구'] = df['지번주소'].str.extract(r'서울특별시\s+(\S+구)')
    df['인허가일자'] = pd.to_datetime(df['인허가일자'], errors='coerce')
    df['폐업일자']   = pd.to_datetime(df['폐업일자'],   errors='coerce')
    df['개업연도']   = df['인허가일자'].dt.year
    df['폐업연도']   = df['폐업일자'].dt.year
    df['영업여부']   = df['영업상태명'] == '영업/정상'

    # 좌표 변환
    has_xy = df['좌표정보(X)'].notna() & df['좌표정보(Y)'].notna()
    coords = df[has_xy].apply(
        lambda r: tm_to_wgs84(r['좌표정보(X)'], r['좌표정보(Y)']), axis=1
    )
    df.loc[has_xy, 'lat'] = coords.apply(lambda c: c[0])
    df.loc[has_xy, 'lng'] = coords.apply(lambda c: c[1])

    # 서울 범위 내 좌표만 유지
    df.loc[~((df['lat'].between(37.4,37.75)) & (df['lng'].between(126.7,127.3))), ['lat','lng']] = np.nan
    return df


@st.cache_data(show_spinner=False)
def build_region_summary(_raw):
    TOP_GU = _raw[_raw['자치구'].notna()]['자치구'].value_counts().head(10).index.tolist()
    rows = []
    for gu in TOP_GU:
        sub = _raw[_raw['자치구'] == gu]
        active = int(sub['영업여부'].sum())
        closed_n = int((~sub['영업여부']).sum())
        # 구 중심 좌표
        sub_xy = sub[sub['lat'].notna()]
        if len(sub_xy) > 10:
            lat_c = float(sub_xy['lat'].median())
            lng_c = float(sub_xy['lng'].median())
        else:
            lat_c, lng_c = None, None

        # 연도별 개폐업 (2015~2024)
        trend_rows = []
        for yr in range(2015, 2025):
            o = int((sub['개업연도'] == yr).sum())
            c = int((sub['폐업연도'] == yr).sum())
            trend_rows.append({'year': yr, 'open': o, 'close': c})

        # SRS 계산 — 실제 데이터 분포 기반 정규화
        total_open  = int((sub['개업연도'].between(2022, 2024)).sum())
        total_close = int((sub['폐업연도'].between(2022, 2024)).sum())
        closure_rate = total_close / max(total_open, 1)

        # 구 면적 (공식 행정구역 면적 km²)
        GU_AREA = {
            '강남구':39.5,'강동구':24.5,'서초구':46.9,'송파구':33.9,
            '마포구':23.8,'영등포구':24.5,'강서구':41.4,'중구':9.96,
            '양천구':17.4,'노원구':35.4,
        }
        area = GU_AREA.get(gu, 25.0)
        density = active / area  # 개/km²

        # 성장률 (2023 → 2024 개업 증감)
        o23 = int((sub['개업연도'] == 2023).sum())
        o24 = int((sub['개업연도'] == 2024).sum())
        growth = (o24 - o23) / max(o23, 1)

        # ── 실제 데이터 범위 기반 Min-Max 정규화 ──
        # 폐업률: 실측 범위 0.96 ~ 1.27 → 0~100점 (높을수록 위험)
        CR_MIN, CR_MAX = 0.90, 1.30
        cr_score = max(0.0, min(1.0, (closure_rate - CR_MIN) / (CR_MAX - CR_MIN))) * 100

        # 밀집도: 실측 범위 4.2 ~ 16.4 /km² → 0~100점 (높을수록 위험)
        D_MIN, D_MAX = 3.0, 18.0
        d_score = max(0.0, min(1.0, (density - D_MIN) / (D_MAX - D_MIN))) * 100

        # 성장률: -0.17 ~ +1.27 → 음수(감소)일수록 위험, 0~100점
        G_MIN, G_MAX = -0.30, 0.50
        g_norm = max(0.0, min(1.0, (growth - G_MIN) / (G_MAX - G_MIN)))
        g_score = (1.0 - g_norm) * 100  # 성장 낮을수록 위험

        # 가중 합산: 폐업률 40% + 밀집도 35% + 성장패널티 25%
        raw_srs = cr_score * 0.40 + d_score * 0.35 + g_score * 0.25
        srs = float(min(max(round(raw_srs, 1), 0), 100))

        if   srs >= 65: grade, cls = "고위험", "danger"
        elif srs >= 50: grade, cls = "주의",   "caution"
        elif srs >= 35: grade, cls = "보통",   "ok"
        else:           grade, cls = "유망",   "safe"

        survival = round(active / max(active + closed_n, 1), 3)

        rows.append({
            'region': gu, 'lat': lat_c, 'lng': lng_c,
            'active': active, 'closed': closed_n,
            'open_24': o24, 'close_24': int((sub['폐업연도']==2024).sum()),
            'srs': srs, 'grade': grade, 'cls': cls,
            'survival': survival,
            'closure_rate': round(closure_rate, 3),
            'density': round(density, 1),
            'growth': round(growth, 3),
            'area': area,
            'trend': trend_rows,
        })
    return rows


# ── 데이터 로드 ──
try:
    raw_df  = load_raw()
    regions = build_region_summary(raw_df)
    DATA_OK = True
except FileNotFoundError:
    DATA_OK = False
    st.error("⚠️ `서울시_제과점영업_인허가_정보.csv` 파일을 앱 디렉토리에 위치시켜 주세요.")
    st.stop()

region_list = [r['region'] for r in regions]
region_map  = {r['region']: r for r in regions}

def get_trend_df(region):
    return pd.DataFrame(region_map[region]['trend'])

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
if "sel" not in st.session_state:
    st.session_state["sel"] = region_list[0]

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="wm">
        <div class="wm-title">🥐 BakeMap</div>
        <div class="wm-sub">베이커리 상권 분석 플랫폼</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slabel">분석 지역 선택</div>', unsafe_allow_html=True)
    st.selectbox("지역", region_list, key="sel", label_visibility="collapsed")

    sel  = st.session_state["sel"]
    info = region_map[sel]
    cls  = info['cls']
    srs  = info['srs']

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown('<div class="slabel">필터</div>', unsafe_allow_html=True)
    risk_range = st.slider("SRS 위험도 범위", 0, 100, (0, 100), step=5, label_visibility="collapsed")
    min_active = st.slider("최소 영업 매장 수", 0, 500, 0, step=20, label_visibility="collapsed")
    st.caption("위험도 범위 · 최소 영업 매장 수")

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    items_html = "".join(
        f'<div class="srow"><span class="skey">{k}</span>'
        f'<span style="font-weight:700;color:#1C1917;">{v}</span></div>'
        for k, v in [
            ("SRS 점수",  f"{srs:.1f} / 100"),
            ("영업 매장", f"{info['active']:,}개"),
            ("폐업 매장", f"{info['closed']:,}개"),
            ("2024 개업", f"{info['open_24']}건"),
            ("2024 폐업", f"{info['close_24']}건"),
            ("생존율",    f"{int(info['survival']*100)}%"),
        ]
    )
    st.markdown(f"""
    <div>
        <div style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                    color:#A8A29E;margin-bottom:9px;">선택 지역 요약</div>
        <div style="font-family:'Lora',serif;font-size:18px;color:#1C1917;margin-bottom:7px;">{sel}</div>
        <span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span>
        <div style="margin-top:12px;">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#C0B9B3;line-height:1.8;">
    출처: 서울 열린데이터 광장<br>서울시 제과점영업 인허가 정보<br>
    <span style="color:#B0A89E;">총 {total:,}건 · 영업 {active:,} / 폐업 {closed:,}</span>
    </div>
    """.format(
        total=len(raw_df),
        active=int(raw_df['영업여부'].sum()),
        closed=int((~raw_df['영업여부']).sum()),
    ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
sel  = st.session_state["sel"]
info = region_map[sel]
cls  = info['cls']
srs  = info['srs']
rt   = get_trend_df(sel)
latest   = rt[rt['year'] == 2024].iloc[0]
prev_yr  = rt[rt['year'] == 2023].iloc[0]
open_d   = int(latest['open']  - prev_yr['open'])
close_d  = int(latest['close'] - prev_yr['close'])
net      = int(latest['open']  - latest['close'])

filtered_regions = [
    r for r in regions
    if risk_range[0] <= r['srs'] <= risk_range[1]
    and r['active'] >= min_active
]

# 페이지 헤더
st.markdown(f"""
<div class="eyebrow">서울시 제과점영업 인허가 공공데이터 기반 · 2015–2024</div>
<div class="ptitle">{sel} <em>베이커리 상권 분석</em></div>
<div class="pdesc">총 {len(raw_df):,}건의 실제 인허가 데이터를 기반으로 산출한 창업 위험도 리포트</div>
""", unsafe_allow_html=True)

# KPI 카드
def dc(d, reverse=False):
    up = (d >= 0) if not reverse else (d <= 0)
    return "up" if up else "down"
def da(d): return "▲" if d >= 0 else "▼"

st.markdown(f"""
<div class="krow">
  <div class="kcard hl">
    <div class="klabel">창업 위험도 SRS</div>
    <div class="kval amber">{srs:.1f}<span style="font-size:14px;color:#B8622A;opacity:.55;"> /100</span></div>
    <div style="margin-top:7px;"><span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span></div>
  </div>
  <div class="kcard">
    <div class="klabel">영업 중 매장</div>
    <div class="kval">{info['active']:,}</div>
    <div class="kdelta">현재 영업 중인 제과·베이커리</div>
  </div>
  <div class="kcard">
    <div class="klabel">2024 신규 개업</div>
    <div class="kval">{int(latest['open'])}</div>
    <div class="kdelta {dc(open_d)}">{da(open_d)} {abs(open_d)} 전년 대비</div>
  </div>
  <div class="kcard">
    <div class="klabel">2024 폐업</div>
    <div class="kval">{int(latest['close'])}</div>
    <div class="kdelta {dc(close_d, reverse=True)}">{da(close_d)} {abs(close_d)} 전년 대비</div>
  </div>
  <div class="kcard">
    <div class="klabel">순 증감 (2024)</div>
    <div class="kval">{'+' if net>=0 else ''}{net}</div>
    <div class="kdelta {'up' if net>=0 else 'down'}">개업 − 폐업</div>
  </div>
  <div class="kcard">
    <div class="klabel">영업 생존율</div>
    <div class="kval">{int(info['survival']*100)}%</div>
    <div class="kdelta">현재 영업 / 전체 인허가</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "  🗺 지도 & 분포  ",
    "  📈 개·폐업 추이  ",
    "  🔁 다지역 비교  ",
    "  🏆 추천 상권  ",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 1 — 지도 & 분포
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    c_map, c_right = st.columns([3, 2], gap="large")

    with c_map:
        st.markdown('<div class="slabel">서울시 구별 상권 지도</div>', unsafe_allow_html=True)

        map_mode = st.radio(
            "지도 표시",
            ["상권 요약", "개별 매장 (선택 구)"],
            horizontal=True, label_visibility="collapsed",
        )

        m = folium.Map(location=[37.54, 126.99], zoom_start=11, tiles="cartodbpositron")

        if map_mode == "개별 매장 (선택 구)":
            sub_stores = raw_df[
                (raw_df['자치구'] == sel) &
                raw_df['lat'].notna()
            ].sample(min(300, len(raw_df[raw_df['자치구']==sel])), random_state=42)
            for _, row in sub_stores.iterrows():
                color = CB if row['영업여부'] else CR
                folium.CircleMarker(
                    location=[row['lat'], row['lng']],
                    radius=4, color=color, fill=True, fill_color=color,
                    fill_opacity=0.65, weight=1,
                    tooltip=f"{'영업 중' if row['영업여부'] else '폐업'} · {str(row['사업장명'])[:15]} · {row['개업연도']:.0f}년 개업",
                ).add_to(m)
            legend_html = """<div style="position:fixed;bottom:16px;left:16px;z-index:1000;background:white;
                padding:10px 14px;border-radius:10px;border:1px solid #E7E4DF;
                font-family:'Noto Sans KR',sans-serif;font-size:12px;box-shadow:0 2px 6px rgba(0,0,0,.08);">
                <b>매장 상태</b><br><span style="color:#3B82F6;">●</span> 영업 중 &nbsp;
                <span style="color:#EF4444;">●</span> 폐업</div>"""
            m.get_root().html.add_child(folium.Element(legend_html))
        else:
            for r in filtered_regions:
                if r['lat'] is None: continue
                is_sel = r['region'] == sel
                c = CMAP[r['cls']]
                radius = max(8, min(35, r['active'] / 12))
                folium.CircleMarker(
                    location=[r['lat'], r['lng']],
                    radius=float(radius),
                    color=c, fill=True, fill_color=c,
                    fill_opacity=0.55 if is_sel else 0.35,
                    weight=3 if is_sel else 1.5,
                    tooltip=folium.Tooltip(
                        f"<b>{r['region']}</b> · SRS {r['srs']:.1f}점 ({r['grade']})<br>"
                        f"영업 {r['active']:,}개 | 2024 개업 {r['open_24']} / 폐업 {r['close_24']}",
                        style="font-family:'Noto Sans KR',sans-serif;font-size:12px;"
                    ),
                ).add_to(m)
                folium.Marker(
                    location=[r['lat'] + 0.004, r['lng']],
                    icon=folium.DivIcon(
                        html=f'<div style="font-family:Noto Sans KR;font-size:11px;font-weight:700;'
                             f'color:{c};white-space:nowrap;text-shadow:0 1px 3px rgba(255,255,255,.9);">'
                             f'{r["region"]}</div>',
                        icon_size=(70, 16), icon_anchor=(35, 0)
                    )
                ).add_to(m)

        st_folium(m, width="100%", height=430, key="map_main")

    with c_right:
        st.markdown('<div class="slabel">구별 SRS 위험도</div>', unsafe_allow_html=True)
        df_s = pd.DataFrame(filtered_regions).sort_values("srs")
        bar_clrs = [CMAP[r] if n == sel else CM for n, r in zip(df_s["region"], df_s["cls"])]

        fig_srs = go.Figure(go.Bar(
            x=list(df_s["srs"]), y=list(df_s["region"]),
            orientation="h", marker_color=bar_clrs,
            text=[f"{v:.1f}" for v in df_s["srs"]],
            textposition="outside",
            textfont=dict(size=11, color="#1C1917"),
        ))
        fig_srs.add_vline(x=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
                          annotation_text="유망", annotation_font_size=10,
                          annotation_font_color="rgba(22,163,74,0.9)")
        fig_srs.add_vline(x=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                          annotation_text="위험", annotation_font_size=10,
                          annotation_font_color="rgba(185,28,28,0.9)")
        fig_srs.update_layout(**lay(height=270,
            xaxis=dict(**AX, range=[0, 120]),
            yaxis=dict(**AX),
            margin=dict(l=0, r=36, t=10, b=0)))
        st.plotly_chart(fig_srs, use_container_width=True)

        # 인사이트
        st.markdown('<div class="slabel">데이터 인사이트</div>', unsafe_allow_html=True)
        r3 = rt[rt['year'] >= 2022]
        cgt = int((r3['close'] > r3['open']).sum())
        if cgt >= 2:
            ic, it = "ins-warn", f"최근 3년 중 <b>{cgt}년</b> 연속 폐업 &gt; 개업. 상권 포화 또는 수요 위축 신호입니다."
        elif srs <= 35:
            ic, it = "ins-good", "폐업률이 낮고 개업이 안정적으로 증가 중인 <b>유망 상권</b>입니다."
        else:
            ic, it = "ins-neut", "개업·폐업이 균형을 이루는 <b>안정 국면</b>. 경쟁 강도를 추가 확인하세요."
        st.markdown(f'<div class="insight {ic}">{it}</div>', unsafe_allow_html=True)

        # 영업/폐업 도넛
        st.markdown('<div class="slabel">영업 현황 비율</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["영업 중", "폐업"],
            values=[info['active'], info['closed']],
            hole=0.62, marker_colors=[CB, CR],
            textfont_size=11, showlegend=True,
        ))
        fig_pie.update_layout(**lay(height=170, margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                        xanchor="center", x=0.5, font_size=11, bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig_pie, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 2 — 개·폐업 추이
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    l2, r2 = st.columns([5, 2], gap="large")

    with l2:
        st.markdown('<div class="slabel">연도별 개·폐업 현황 (2015–2024)</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="data-note">📌 실제 서울시 제과점영업 인허가 데이터 기반 · {sel} 전체</div>',
            unsafe_allow_html=True
        )
        net_s = rt["open"] - rt["close"]

        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(x=list(rt["year"]), y=list(rt["open"]),
                               name="개업", marker_color=CB, opacity=0.85))
        fig_t.add_trace(go.Bar(x=list(rt["year"]), y=list(-rt["close"]),
                               name="폐업", marker_color=CR, opacity=0.85))
        fig_t.add_trace(go.Scatter(
            x=list(rt["year"]), y=list(net_s),
            mode="lines+markers", name="순증감",
            line=dict(color=CA, width=2.5),
            marker=dict(size=7, color=CA, line=dict(color="#FFFFFF", width=2)),
        ))
        fig_t.update_layout(**lay(barmode="overlay", height=300,
            xaxis=dict(**AX, tickmode="linear", dtick=1),
            yaxis=dict(**AX, zeroline=True, zerolinecolor="#E7E4DF")))
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="slabel" style="margin-top:16px;">누적 순증감</div>', unsafe_allow_html=True)
        rt2 = rt.copy()
        rt2["cum"] = (rt2["open"] - rt2["close"]).cumsum()
        lc = CG if float(rt2["cum"].iloc[-1]) >= 0 else CR
        fc = "rgba(34,197,94,0.08)" if lc == CG else "rgba(239,68,68,0.08)"
        fig_c = go.Figure(go.Scatter(
            x=list(rt2["year"]), y=list(rt2["cum"]),
            fill="tozeroy", fillcolor=fc,
            line=dict(color=lc, width=2), mode="lines+markers",
            marker=dict(size=6, color=lc, line=dict(color="#FFFFFF", width=2)),
        ))
        fig_c.update_layout(**lay(height=175,
            xaxis=dict(**AX, tickmode="linear", dtick=1),
            yaxis=dict(**AX, zeroline=True, zerolinecolor="#E7E4DF")))
        st.plotly_chart(fig_c, use_container_width=True)

    with r2:
        st.markdown('<div class="slabel">기간 요약 (2015–2024)</div>', unsafe_allow_html=True)
        po = int(rt["open"].sum()); pc = int(rt["close"].sum()); pn = po - pc
        for k, v, sc in [
            ("기간 총 개업",  f"{po:,}건",  ""),
            ("기간 총 폐업",  f"{pc:,}건",  ""),
            ("순 증감",       f"{'+' if pn>=0 else ''}{pn}건", "up" if pn>=0 else "down"),
            ("폐업률 (3년)",  f"{round(info['closure_rate']*100)}%", ""),
            ("영업 생존율",   f"{int(info['survival']*100)}%", ""),
            ("밀집도",        f"{info['density']:.1f}개/km²", ""),
        ]:
            vc = "#16A34A" if sc=="up" else "#DC2626" if sc=="down" else "#1C1917"
            st.markdown(
                f'<div class="srow"><span class="skey">{k}</span>'
                f'<span style="color:{vc};font-weight:700;font-size:13px;">{v}</span></div>',
                unsafe_allow_html=True)

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="slabel">SRS 위험도 게이지</div>', unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=srs,
            number={"suffix": "점", "font": {"size": 24, "color": "#1C1917", "family": "Lora, serif"}},
            gauge={
                "axis": {"range": [0, 100], "tickvals": [], "tickwidth": 0},
                "bar": {"color": CMAP[cls], "thickness": 0.22},
                "bgcolor": "#EDE9E4", "borderwidth": 0,
                "steps": [
                    {"range": [0,  35], "color": "rgba(34,197,94,0.12)"},
                    {"range": [35, 65], "color": "rgba(234,179,8,0.10)"},
                    {"range": [65,100], "color": "rgba(239,68,68,0.10)"},
                ],
            },
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                            font_family="Noto Sans KR, sans-serif",
                            height=155, margin=dict(l=10,r=10,t=10,b=0))
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:-8px;">'
            f'<span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span></div>',
            unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 3 — 다지역 비교
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.markdown('<div class="slabel">비교할 지역 선택 (최대 6개)</div>', unsafe_allow_html=True)
    compare_regions = st.multiselect(
        "지역 선택", region_list,
        default=region_list[:5], max_selections=6,
        label_visibility="collapsed",
    )

    if not compare_regions:
        st.info("비교할 지역을 하나 이상 선택하세요.")
    else:
        cmp = [r for r in regions if r['region'] in compare_regions]
        cmp_sorted = sorted(cmp, key=lambda r: r['srs'])

        # 테이블
        st.markdown('<div class="slabel">핵심 지표 비교</div>', unsafe_allow_html=True)
        rows_html = ""
        for r in cmp_sorted:
            is_sel = r['region'] == sel
            bg = "background:#FEF5EE;" if is_sel else ""
            rows_html += (
                f'<tr style="{bg}">'
                f'<td><b>{r["region"]}</b>{"  ★" if is_sel else ""}</td>'
                f'<td><span class="bdg {BDGCLS[r["cls"]]}">{GLABEL[r["cls"]]}</span></td>'
                f'<td style="font-family:\'Lora\',serif;font-size:15px;">{r["srs"]:.1f}</td>'
                f'<td>{r["active"]:,}</td>'
                f'<td>{r["open_24"]}</td>'
                f'<td>{r["close_24"]}</td>'
                f'<td>{int(r["survival"]*100)}%</td>'
                f'<td>{r["density"]:.1f}</td>'
                f'</tr>'
            )
        st.markdown(f"""
        <table class="cmp-table">
          <thead><tr>
            <th>자치구</th><th>등급</th><th>SRS</th>
            <th>영업 매장</th><th>2024 개업</th><th>2024 폐업</th>
            <th>생존율</th><th>밀집도/km²</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 개폐업 비교 차트
        st.markdown('<div class="slabel">2024년 개·폐업 비교</div>', unsafe_allow_html=True)
        cmp_df = pd.DataFrame(cmp_sorted)
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            x=list(cmp_df["region"]), y=list(cmp_df["open_24"]),
            name="개업", marker_color=CB, opacity=0.85,
        ))
        fig_cmp.add_trace(go.Bar(
            x=list(cmp_df["region"]), y=list(cmp_df["close_24"]),
            name="폐업", marker_color=CR, opacity=0.85,
        ))
        fig_cmp.update_layout(**lay(barmode="group", height=270,
            xaxis=dict(**AX), yaxis=dict(**AX)))
        st.plotly_chart(fig_cmp, use_container_width=True)

        # 추이 오버레이 (선택 구들)
        st.markdown('<div class="slabel">연도별 개업 추이 비교 (2015–2024)</div>', unsafe_allow_html=True)
        COLORS = [CB, CR, CG, CY, CA, "#8B5CF6"]
        fig_ol = go.Figure()
        for i, r in enumerate(cmp_sorted[:6]):
            t = get_trend_df(r['region'])
            fig_ol.add_trace(go.Scatter(
                x=list(t["year"]), y=list(t["open"]),
                mode="lines+markers", name=r['region'],
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                marker=dict(size=5),
            ))
        fig_ol.update_layout(**lay(height=270,
            xaxis=dict(**AX, tickmode="linear", dtick=1),
            yaxis=dict(**AX)))
        st.plotly_chart(fig_ol, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 4 — 추천 상권
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    top_recs = sorted(
        [r for r in filtered_regions if r['region'] != sel],
        key=lambda r: r['srs']
    )[:5]

    def reason(r):
        parts = []
        if r['closure_rate'] < 0.55:  parts.append("낮은 폐업률")
        if r['growth'] > 0.03:        parts.append("개업 증가 추세")
        if r['density'] < 12:         parts.append("낮은 경쟁 밀도")
        if r['survival'] > 0.2:       parts.append("상대적 높은 생존율")
        if r['open_24'] > 40:         parts.append("활발한 신규 진입")
        return " + ".join(parts) if parts else "종합 리스크 양호"

    st.markdown(f'<div class="slabel">{sel} 대비 추천 TOP 5 (필터 적용)</div>', unsafe_allow_html=True)

    if not top_recs:
        st.info("현재 필터 조건을 만족하는 추천 지역이 없습니다. 사이드바 필터를 조정해보세요.")
    else:
        for rank, r in enumerate(top_recs, 1):
            diff = srs - r['srs']
            diff_html = (
                f'<span style="color:#16A34A;font-weight:700;">▼ {diff:.1f}점 낮음</span>'
                if diff > 0 else
                f'<span style="color:#DC2626;font-weight:700;">▲ {abs(diff):.1f}점 높음</span>'
            )
            st.markdown(f"""
            <div class="rec-card">
              <div>
                <div class="rec-name">#{rank} &nbsp; {r['region']}</div>
                <div class="rec-reason">✔ {reason(r)}</div>
                <div style="margin-top:6px;">
                  <span class="bdg {BDGCLS[r['cls']]}">{GLABEL[r['cls']]}</span>
                  &nbsp; {diff_html}
                </div>
              </div>
              <div style="text-align:right;min-width:90px;">
                <div style="font-family:'Lora',serif;font-size:24px;color:{CMAP[r['cls']]};font-weight:700;">{r['srs']:.1f}</div>
                <div style="font-size:11px;color:#A8A29E;margin-top:2px;">SRS 점수</div>
                <div style="font-size:12px;color:#1C1917;margin-top:4px;font-weight:600;">영업 {r['active']:,}개</div>
                <div style="font-size:11px;color:#A8A29E;">2024 개업 {r['open_24']}건</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="slabel">전체 구 SRS 순위 (필터 적용)</div>', unsafe_allow_html=True)
    all_s = sorted(filtered_regions, key=lambda r: r['srs'])
    fig_all = go.Figure(go.Bar(
        x=[r['region'] for r in all_s],
        y=[r['srs'] for r in all_s],
        marker_color=[CMAP[r['cls']] if r['region'] != sel else CA for r in all_s],
        text=[f"{r['srs']:.1f}" for r in all_s],
        textposition="outside",
        textfont=dict(size=12, color="#1C1917"),
    ))
    fig_all.add_hline(y=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
                      annotation_text="유망 35점", annotation_font_size=11,
                      annotation_font_color="rgba(22,163,74,0.8)")
    fig_all.add_hline(y=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                      annotation_text="위험 65점", annotation_font_size=11,
                      annotation_font_color="rgba(185,28,28,0.8)")
    fig_all.update_layout(**lay(height=280,
        xaxis=dict(**AX), yaxis=dict(**AX, range=[0, 110]),
        margin=dict(l=0, r=0, t=20, b=0)))
    st.plotly_chart(fig_all, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown('<hr class="hr">', unsafe_allow_html=True)
bc, tc = st.columns([1, 3])
with bc:
    if st.button("📄 PDF 리포트 생성", use_container_width=True):
        st.toast("🔒 비즈니스 플랜 구독 후 이용 가능합니다.", icon="📄")
with tc:
    st.markdown("""
    <div style="font-size:12px;color:#A8A29E;padding-top:11px;line-height:1.9;">
    상권 요약 · 시계열 차트 · SRS 점수 · 추천 지역이 포함된 PDF 리포트를 생성합니다.<br>
    창업 계획서 · 투자 제안서 · 금융기관 대출 심사 서류에 활용 가능합니다.
    </div>
    """, unsafe_allow_html=True)
