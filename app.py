import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import date, timedelta
import random

st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Lora:wght@600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1C1917; }

.stApp { background: #F8F6F2; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E7E4DF;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] { display: none !important; }

#MainMenu, header, footer { visibility: hidden; }
.block-container { padding: 1.8rem 2rem 2rem; }

/* ── 워드마크 ── */
.wm { padding: 22px 16px 16px; border-bottom: 1px solid #F0EDE8; margin-bottom: 18px; }
.wm-title { font-family: 'Lora', serif; font-size: 20px; color: #B8622A; letter-spacing: -0.01em; }
.wm-sub   { font-size: 10px; font-weight: 600; color: #B0A89E; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 3px; }

/* ── 페이지 헤더 ── */
.eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #B8622A; margin-bottom: 5px; }
.ptitle  { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; line-height: 1.2; margin-bottom: 4px; }
.ptitle em { color: #B8622A; font-style: normal; }
.pdesc   { font-size: 13px; color: #6B6560; margin-bottom: 20px; }

/* ── KPI 카드 ── */
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

/* ── 배지 ── */
.bdg { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.bdg-safe    { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.bdg-ok      { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.bdg-caution { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }
.bdg-danger  { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }

/* ── 섹션 레이블 ── */
.slabel {
    font-size: 10px; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    color: #A8A29E; margin-bottom: 12px; display: flex; align-items: center; gap: 7px;
}
.slabel::before { content:''; display:inline-block; width:3px; height:10px; background:#B8622A; border-radius:2px; }

/* ── 구분선 ── */
.hr { border: none; border-top: 1px solid #E7E4DF; margin: 16px 0; }

/* ── 사이드 통계 행 ── */
.srow { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid #F0EDE8; font-size:13px; }
.srow:last-child { border-bottom:none; }
.skey { color: #78716C; }

/* ── 인사이트 박스 ── */
.insight { border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.65; }
.ins-good { background: #F0FDF4; border-left: 3px solid #22C55E; color: #14532D; }
.ins-warn { background: #FFF7ED; border-left: 3px solid #F97316; color: #7C2D12; }
.ins-neut { background: #FEFCE8; border-left: 3px solid #EAB308; color: #713F12; }

/* ── 추천 카드 ── */
.rec-card {
    background: #FFFFFF; border: 1px solid #E7E4DF;
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: flex-start;
}
.rec-card:hover { border-color: #B8622A; background: #FEF5EE; }
.rec-name { font-size: 15px; font-weight: 700; color: #1C1917; margin-bottom: 4px; }
.rec-reason { font-size: 12px; color: #78716C; line-height: 1.5; }

/* ── 비교 테이블 ── */
.cmp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cmp-table th { background: #F5F2EE; padding: 10px 14px; text-align: left; font-weight: 700; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: #78716C; border-bottom: 2px solid #E7E4DF; }
.cmp-table td { padding: 10px 14px; border-bottom: 1px solid #F0EDE8; color: #1C1917; font-weight: 500; }
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-table tr:hover td { background: #FAF8F5; }

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] { background: #EDE9E4; border-radius: 10px; padding: 3px; gap: 0; border: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; padding: 7px 15px !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #78716C !important; letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] { background: #FFFFFF !important; color: #1C1917 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }

/* ── selectbox ── */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #FFFFFF !important; border: 1px solid #E7E4DF !important;
    border-radius: 10px !important; color: #1C1917 !important;
}

/* ── slider ── */
.stSlider [data-baseweb="slider"] { padding: 0 4px; }

/* ── 버튼 ── */
.stButton > button {
    background: #B8622A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 10px 20px !important;
    box-shadow: 0 2px 6px rgba(184,98,42,0.28) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── 지도 ── */
iframe { border-radius: 12px; }
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
AX  = dict(gridcolor="#EDE9E4", tickfont_size=11, showline=False)

def lay(**kw): return {**BASE, **kw}

CA="#B8622A"; CB="#3B82F6"; CR="#EF4444"; CG="#22C55E"; CY="#EAB308"; CM="#D6D3CE"
CMAP   = {"safe": CG, "ok": CY, "caution": CA, "danger": CR}
BDGCLS = {"safe": "bdg-safe", "ok": "bdg-ok", "caution": "bdg-caution", "danger": "bdg-danger"}
GLABEL = {"safe": "유망 ↑", "ok": "보통", "caution": "주의 ↓", "danger": "고위험 ✕"}

# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════
REGION_META = {
    "연남동":  {"lat": 37.5612, "lng": 126.9236, "area": 0.82},
    "성수동":  {"lat": 37.5443, "lng": 127.0557, "area": 1.21},
    "한남동":  {"lat": 37.5349, "lng": 127.0013, "area": 0.95},
    "방배동":  {"lat": 37.4831, "lng": 126.9913, "area": 1.45},
    "망원동":  {"lat": 37.5562, "lng": 126.9012, "area": 0.73},
    "홍대앞":  {"lat": 37.5570, "lng": 126.9237, "area": 0.68},
    "이태원동":{"lat": 37.5345, "lng": 126.9942, "area": 0.91},
    "압구정동":{"lat": 37.5270, "lng": 127.0282, "area": 1.12},
}

@st.cache_data
def build_store_df():
    random.seed(42); np.random.seed(42)
    rows = []
    store_id = 1
    for region, meta in REGION_META.items():
        n_stores = random.randint(14, 42)
        for _ in range(n_stores):
            open_yr  = random.randint(2015, 2024)
            open_mo  = random.randint(1, 12)
            open_dt  = date(open_yr, open_mo, 1)
            is_closed = random.random() < 0.38
            if is_closed:
                dur = random.randint(8, 36)
                close_dt = open_dt + timedelta(days=dur * 30)
                if close_dt > date.today(): close_dt = date.today() - timedelta(days=10)
                status = "closed"
            else:
                close_dt = None
                status   = "open"
            lat = meta["lat"] + np.random.uniform(-0.004, 0.004)
            lng = meta["lng"] + np.random.uniform(-0.005, 0.005)
            rows.append({
                "id": store_id, "region": region,
                "lat": lat, "lng": lng,
                "open_date": open_dt, "close_date": close_dt,
                "status": status,
            })
            store_id += 1
    return pd.DataFrame(rows)


@st.cache_data
def build_trend_df():
    np.random.seed(7)
    PROFILES = {
        "연남동":   {"bo": 8,  "bc": 5,  "dir": "decline"},
        "성수동":   {"bo": 6,  "bc": 2,  "dir": "growth"},
        "한남동":   {"bo": 6,  "bc": 4,  "dir": "stable"},
        "방배동":   {"bo": 5,  "bc": 4,  "dir": "stable"},
        "망원동":   {"bo": 7,  "bc": 1,  "dir": "growth"},
        "홍대앞":   {"bo": 9,  "bc": 6,  "dir": "decline"},
        "이태원동": {"bo": 5,  "bc": 5,  "dir": "decline"},
        "압구정동": {"bo": 4,  "bc": 2,  "dir": "stable"},
    }
    rows = []
    for r, p in PROFILES.items():
        for i, yr in enumerate(range(2019, 2026)):
            if p["dir"] == "growth":
                o = max(1, int(p["bo"] + i*1.4 + np.random.randn()*1.2))
                c = max(0, int(p["bc"] + i*0.2 + np.random.randn()*0.8))
            elif p["dir"] == "decline":
                o = max(1, int(p["bo"] - i*0.7 + np.random.randn()*1.2))
                c = max(0, int(p["bc"] + i*0.9 + np.random.randn()*0.8))
            else:
                o = max(1, int(p["bo"] + np.random.randn()*1.5))
                c = max(0, int(p["bc"] + np.random.randn()*1.0))
            rows.append({"region": r, "year": yr, "open": o, "close": c})
    return pd.DataFrame(rows)


@st.cache_data
def build_region_df(store_df, trend_df):
    rows = []
    for region, meta in REGION_META.items():
        rd  = store_df[store_df["region"] == region]
        rt  = trend_df[trend_df["region"] == region]
        stores_open   = int((rd["status"] == "open").sum())
        stores_closed = int((rd["status"] == "closed").sum())
        recent = rt[rt["year"] >= 2023]
        total_open  = int(recent["open"].sum())
        total_close = int(recent["close"].sum())
        closure_rate = total_close / max(total_open, 1)
        density = stores_open / meta["area"]
        density_norm = min(density / 30, 1.0)
        lt = rt[rt["year"] == 2025].iloc[0]
        pr = rt[rt["year"] == 2024].iloc[0]
        growth = (lt["open"] - pr["open"]) / max(pr["open"], 1)
        growth_pen = max(-growth, 0)
        raw = closure_rate * 40 + density_norm * 35 * 100 + growth_pen * 25 * 100
        srs = float(min(max(round(raw, 1), 0), 100))
        if   srs >= 65: grade, cls = "고위험", "danger"
        elif srs >= 50: grade, cls = "주의",   "caution"
        elif srs >= 35: grade, cls = "보통",   "ok"
        else:           grade, cls = "유망",   "safe"
        survival = round(1 - stores_closed / max(stores_open + stores_closed, 1), 2)
        rows.append({
            "region": region,
            "lat": meta["lat"], "lng": meta["lng"],
            "stores_open": stores_open,
            "stores_closed": stores_closed,
            "recent_open": int(lt["open"]),
            "recent_close": int(lt["close"]),
            "srs": srs, "grade": grade, "cls": cls,
            "survival": survival,
            "closure_rate": round(closure_rate, 3),
            "density": round(density, 1),
            "growth": round(growth, 3),
        })
    return pd.DataFrame(rows)


store_df  = build_store_df()
trend_df  = build_trend_df()
region_df = build_region_df(store_df, trend_df)
region_list = region_df["region"].tolist()

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

    selected = st.session_state["sel"]
    info = region_df[region_df["region"] == selected].iloc[0]
    cls  = str(info["cls"])
    srs  = float(info["srs"])

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown('<div class="slabel">필터</div>', unsafe_allow_html=True)
    risk_range = st.slider("SRS 위험도 범위", 0, 100, (0, 100), step=5, label_visibility="collapsed")
    min_stores = st.slider("최소 매장 수", 0, 50, 0, step=5, label_visibility="collapsed")
    st.caption("위험도 · 최소 매장 수 필터")

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    items_html = "".join(
        f'<div class="srow"><span class="skey">{k}</span>'
        f'<span style="font-weight:700;color:#1C1917;">{v}</span></div>'
        for k, v in [
            ("SRS 점수",    f"{srs:.1f} / 100"),
            ("현재 매장",   f"{int(info['stores_open'])}개"),
            ("폐업 매장",   f"{int(info['stores_closed'])}개"),
            ("최근 개업",   f"{int(info['recent_open'])}건"),
            ("최근 폐업",   f"{int(info['recent_close'])}건"),
            ("생존율",      f"{int(info['survival']*100)}%"),
        ]
    )
    st.markdown(f"""
    <div>
        <div style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                    color:#A8A29E;margin-bottom:9px;">선택 지역 요약</div>
        <div style="font-family:'Lora',serif;font-size:18px;color:#1C1917;margin-bottom:7px;">{selected}</div>
        <span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span>
        <div style="margin-top:12px;">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#C0B9B3;line-height:1.8;">
    데이터: 서울 열린데이터 광장<br>서울시 제과점영업 인허가 정보<br>
    <span style="color:#D6D3CE;">※ 데모 모의 데이터</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN — derive data
# ══════════════════════════════════════════════════════════════
selected  = st.session_state["sel"]
info      = region_df[region_df["region"] == selected].iloc[0]
cls       = str(info["cls"])
srs       = float(info["srs"])
rt        = trend_df[trend_df["region"] == selected].sort_values("year").reset_index(drop=True)
latest    = rt[rt["year"] == 2025].iloc[0]
prev_yr   = rt[rt["year"] == 2024].iloc[0]
open_d    = int(latest["open"]  - prev_yr["open"])
close_d   = int(latest["close"] - prev_yr["close"])
net       = int(latest["open"]  - latest["close"])

# filtered region list for comparison / recommendation
filtered_df = region_df[
    (region_df["srs"].between(*risk_range)) &
    (region_df["stores_open"] >= min_stores)
]

# ── Page header ──
st.markdown(f"""
<div class="eyebrow">상권 분석 리포트 · 서울시 2019–2025</div>
<div class="ptitle">{selected} <em>베이커리 시장</em></div>
<div class="pdesc">서울시 제과점영업 인허가 공공데이터 기반 · 실시간 상권 위험도 분석</div>
""", unsafe_allow_html=True)

# ── KPI row ──
def delta_cls(d, reverse=False):
    up = (d >= 0) if not reverse else (d <= 0)
    return "up" if up else "down"
def delta_arrow(d): return "▲" if d >= 0 else "▼"

net_cls = "up" if net >= 0 else "down"

st.markdown(f"""
<div class="krow">
  <div class="kcard hl">
    <div class="klabel">창업 위험도 SRS</div>
    <div class="kval amber">{srs:.1f}<span style="font-size:14px;color:#B8622A;opacity:.55;"> /100</span></div>
    <div style="margin-top:7px;"><span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span></div>
  </div>
  <div class="kcard">
    <div class="klabel">영업 중 매장</div>
    <div class="kval">{int(info['stores_open'])}</div>
    <div class="kdelta">현재 운영 중인 제과·베이커리</div>
  </div>
  <div class="kcard">
    <div class="klabel">최근 개업</div>
    <div class="kval">{int(latest['open'])}</div>
    <div class="kdelta {delta_cls(open_d)}">{delta_arrow(open_d)} {abs(open_d)} 전년 대비</div>
  </div>
  <div class="kcard">
    <div class="klabel">최근 폐업</div>
    <div class="kval">{int(latest['close'])}</div>
    <div class="kdelta {delta_cls(close_d, reverse=True)}">{delta_arrow(close_d)} {abs(close_d)} 전년 대비</div>
  </div>
  <div class="kcard">
    <div class="klabel">순 증감</div>
    <div class="kval">{'+' if net>=0 else ''}{net}</div>
    <div class="kdelta {net_cls}">개업 − 폐업</div>
  </div>
  <div class="kcard">
    <div class="klabel">생존율</div>
    <div class="kval">{int(info['survival']*100)}%</div>
    <div class="kdelta">누적 추정치</div>
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
        st.markdown('<div class="slabel">지역별 상권 지도</div>', unsafe_allow_html=True)

        show_heatmap = st.toggle("히트맵 레이어 표시", value=False)

        m = folium.Map(location=[37.535, 126.975], zoom_start=12, tiles="cartodbpositron")

        # Individual store markers
        sel_stores = store_df[store_df["region"] == selected]
        for _, row in sel_stores.iterrows():
            color = "#3B82F6" if row["status"] == "open" else "#EF4444"
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=5,
                color=color, fill=True, fill_color=color,
                fill_opacity=0.7, weight=1,
                tooltip=f"{'영업 중' if row['status']=='open' else '폐업'} · 개업 {row['open_date'].year}년",
            ).add_to(m)

        # Region summary circles
        for _, row in region_df.iterrows():
            is_sel = row["region"] == selected
            c = CMAP[row["cls"]]
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=float(row["stores_open"]) * 0.28 + (9 if is_sel else 5),
                color=c, fill=True, fill_color=c,
                fill_opacity=0.25 if is_sel else 0.15,
                weight=3 if is_sel else 1.5,
                tooltip=folium.Tooltip(
                    f"<b>{row['region']}</b> · SRS {row['srs']:.1f}점 ({row['grade']})<br>"
                    f"영업 {row['stores_open']}개 | 개업 {row['recent_open']} / 폐업 {row['recent_close']}",
                    style="font-family:'Noto Sans KR',sans-serif;font-size:12px;"
                ),
            ).add_to(m)

        if show_heatmap:
            from folium.plugins import HeatMap
            heat_data = [[r["lat"], r["lng"], r["stores_open"]] for _, r in region_df.iterrows()]
            HeatMap(heat_data, radius=35, blur=25, min_opacity=0.3).add_to(m)

        # Legend
        legend_html = """
        <div style="position:fixed;bottom:20px;left:20px;z-index:1000;background:white;
                    padding:10px 14px;border-radius:10px;border:1px solid #E7E4DF;
                    font-family:'Noto Sans KR',sans-serif;font-size:12px;box-shadow:0 2px 6px rgba(0,0,0,.08);">
          <b style="color:#1C1917;">매장 상태</b><br>
          <span style="color:#3B82F6;">●</span> 영업 중 &nbsp;
          <span style="color:#EF4444;">●</span> 폐업
        </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, width="100%", height=430, key="map_main")

    with c_right:
        st.markdown('<div class="slabel">SRS 위험도 비교</div>', unsafe_allow_html=True)
        df_s = filtered_df.sort_values("srs")
        bar_clrs = [CMAP[r] if n == selected else CM for n, r in zip(df_s["region"], df_s["cls"])]

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
        fig_srs.update_layout(**lay(height=250,
            xaxis=dict(**AX, range=[0, 115]),
            yaxis=dict(**AX),
            margin=dict(l=0, r=36, t=10, b=0)))
        st.plotly_chart(fig_srs, use_container_width=True)

        st.markdown('<div class="slabel">데이터 인사이트</div>', unsafe_allow_html=True)
        r3 = rt[rt["year"] >= 2023]
        cgt = int((r3["close"] > r3["open"]).sum())
        if cgt >= 2:
            ic, it = "ins-warn", f"최근 3년 중 <b>{cgt}년</b> 연속 폐업 &gt; 개업. 상권 포화 신호입니다."
        elif srs <= 35:
            ic, it = "ins-good", "폐업률이 낮고 개업 증가세가 <b>안정적인 유망 상권</b>입니다."
        else:
            ic, it = "ins-neut", "개업·폐업이 균형을 이루는 <b>안정 국면</b>. 경쟁 강도를 추가 확인하세요."
        st.markdown(f'<div class="insight {ic}">{it}</div>', unsafe_allow_html=True)

        # Mini pie: open vs closed
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<div class="slabel">매장 현황 비율</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["영업 중", "폐업"],
            values=[int(info["stores_open"]), int(info["stores_closed"])],
            hole=0.6,
            marker_colors=[CB, CR],
            textfont_size=11,
            showlegend=True,
        ))
        fig_pie.update_layout(**lay(height=180, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5,
                        font_size=11, bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig_pie, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 2 — 개·폐업 추이
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    l2, r2 = st.columns([5, 2], gap="large")

    with l2:
        st.markdown('<div class="slabel">연도별 개·폐업 현황</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="slabel">기간 요약 (2019–2025)</div>', unsafe_allow_html=True)
        po = int(rt["open"].sum()); pc = int(rt["close"].sum()); pn = po - pc
        for k, v, sc in [
            ("기간 총 개업", f"{po}건", ""),
            ("기간 총 폐업", f"{pc}건", ""),
            ("순 증감",      f"{'+' if pn>=0 else ''}{pn}건", "up" if pn>=0 else "down"),
            ("폐업률",       f"{round(pc/max(po,1)*100)}%", ""),
            ("생존율",       f"{int(info['survival']*100)}%", ""),
        ]:
            vc = "#16A34A" if sc=="up" else "#DC2626" if sc=="down" else "#1C1917"
            st.markdown(
                f'<div class="srow"><span class="skey">{k}</span>'
                f'<span style="color:{vc};font-weight:700;font-size:13px;">{v}</span></div>',
                unsafe_allow_html=True)

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="slabel">위험도 게이지</div>', unsafe_allow_html=True)
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
                            height=155, margin=dict(l=10, r=10, t=10, b=0))
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
    default_compare = region_list[:4]
    compare_regions = st.multiselect(
        "지역 선택", region_list,
        default=default_compare, max_selections=6,
        label_visibility="collapsed",
    )

    if not compare_regions:
        st.info("비교할 지역을 하나 이상 선택하세요.")
    else:
        cmp_df = region_df[region_df["region"].isin(compare_regions)].copy()

        # Summary table
        st.markdown('<div class="slabel" style="margin-top:4px;">지역별 핵심 지표 비교</div>', unsafe_allow_html=True)
        rows_html = ""
        for _, row in cmp_df.sort_values("srs").iterrows():
            is_sel = row["region"] == selected
            bg = "background:#FEF5EE;" if is_sel else ""
            rows_html += (
                f'<tr style="{bg}">'
                f'<td><b>{row["region"]}</b>{"  ★" if is_sel else ""}</td>'
                f'<td><span class="bdg {BDGCLS[row["cls"]]}">{GLABEL[row["cls"]]}</span></td>'
                f'<td style="font-family:\'Lora\',serif;font-size:15px;">{row["srs"]:.1f}</td>'
                f'<td>{int(row["stores_open"])}</td>'
                f'<td>{int(row["recent_open"])}</td>'
                f'<td>{int(row["recent_close"])}</td>'
                f'<td>{int(row["survival"]*100)}%</td>'
                f'<td>{row["density"]:.1f}</td>'
                f'</tr>'
            )
        st.markdown(f"""
        <table class="cmp-table">
          <thead><tr>
            <th>지역</th><th>등급</th><th>SRS</th>
            <th>영업 매장</th><th>최근 개업</th><th>최근 폐업</th>
            <th>생존율</th><th>밀집도/km²</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Grouped bar comparison
        st.markdown('<div class="slabel">개·폐업 비교 차트</div>', unsafe_allow_html=True)
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            x=list(cmp_df.sort_values("srs")["region"]),
            y=list(cmp_df.sort_values("srs")["recent_open"]),
            name="최근 개업", marker_color=CB, opacity=0.85,
        ))
        fig_cmp.add_trace(go.Bar(
            x=list(cmp_df.sort_values("srs")["region"]),
            y=list(cmp_df.sort_values("srs")["recent_close"]),
            name="최근 폐업", marker_color=CR, opacity=0.85,
        ))
        fig_cmp.update_layout(**lay(barmode="group", height=280,
            xaxis=dict(**AX),
            yaxis=dict(**AX)))
        st.plotly_chart(fig_cmp, use_container_width=True)

        # SRS radar-ish: horizontal bars side by side
        st.markdown('<div class="slabel">SRS 점수 비교</div>', unsafe_allow_html=True)
        cmp_s = cmp_df.sort_values("srs")
        fig_cbar = go.Figure(go.Bar(
            x=list(cmp_s["srs"]),
            y=list(cmp_s["region"]),
            orientation="h",
            marker_color=[CMAP[c] for c in cmp_s["cls"]],
            text=[f"{v:.1f}" for v in cmp_s["srs"]],
            textposition="outside",
            textfont=dict(size=12, color="#1C1917"),
        ))
        fig_cbar.add_vline(x=35, line_dash="dot", line_color="rgba(34,197,94,0.5)")
        fig_cbar.add_vline(x=65, line_dash="dot", line_color="rgba(239,68,68,0.5)")
        fig_cbar.update_layout(**lay(height=250,
            xaxis=dict(**AX, range=[0, 115]),
            yaxis=dict(**AX),
            margin=dict(l=0, r=36, t=10, b=0)))
        st.plotly_chart(fig_cbar, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 4 — 추천 상권
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    top_regions = (
        filtered_df[filtered_df["region"] != selected]
        .sort_values("srs")
        .head(5)
    )

    def reason(row):
        parts = []
        if row["closure_rate"] < 0.30:
            parts.append("낮은 폐업률")
        if row["growth"] > 0.05:
            parts.append("개업 증가 추세")
        if row["density"] < 15:
            parts.append("낮은 경쟁 밀도")
        if row["survival"] > 0.65:
            parts.append("높은 생존율")
        if row["stores_open"] >= 20:
            parts.append("검증된 상권 규모")
        return " + ".join(parts) if parts else "종합 리스크 양호"

    st.markdown('<div class="slabel">현재 분석 지역 대비 추천 TOP 5</div>', unsafe_allow_html=True)

    if top_regions.empty:
        st.info("현재 필터 조건을 만족하는 추천 지역이 없습니다. 사이드바의 필터를 조정해 보세요.")
    else:
        for rank, (_, row) in enumerate(top_regions.iterrows(), 1):
            r_label = reason(row)
            diff = srs - row["srs"]
            diff_html = f'<span style="color:#16A34A;font-weight:700;">▼ {diff:.1f}점 낮음</span>' if diff > 0 else ""
            st.markdown(f"""
            <div class="rec-card">
                <div>
                    <div class="rec-name">#{rank} &nbsp; {row['region']}</div>
                    <div class="rec-reason">✔ {r_label}</div>
                    <div style="margin-top:6px;">
                        <span class="bdg {BDGCLS[row['cls']]}">{GLABEL[row['cls']]}</span>
                        &nbsp; {diff_html}
                    </div>
                </div>
                <div style="text-align:right;min-width:80px;">
                    <div style="font-family:'Lora',serif;font-size:24px;color:{CMAP[row['cls']]};font-weight:700;">{row['srs']:.1f}</div>
                    <div style="font-size:11px;color:#A8A29E;margin-top:2px;">SRS 점수</div>
                    <div style="font-size:12px;color:#1C1917;margin-top:4px;font-weight:600;">영업 {int(row['stores_open'])}개</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="slabel">전체 상권 SRS 순위</div>', unsafe_allow_html=True)
    all_s = filtered_df.sort_values("srs")
    fig_all = go.Figure(go.Bar(
        x=list(all_s["region"]),
        y=list(all_s["srs"]),
        marker_color=[CMAP[c] if n != selected else CA
                      for n, c in zip(all_s["region"], all_s["cls"])],
        text=[f"{v:.1f}" for v in all_s["srs"]],
        textposition="outside",
        textfont=dict(size=12, color="#1C1917"),
    ))
    fig_all.add_hline(y=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
                      annotation_text="유망 기준 35점", annotation_font_size=11,
                      annotation_font_color="rgba(22,163,74,0.8)")
    fig_all.add_hline(y=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                      annotation_text="위험 기준 65점", annotation_font_size=11,
                      annotation_font_color="rgba(185,28,28,0.8)")
    fig_all.update_layout(**lay(height=300,
        xaxis=dict(**AX),
        yaxis=dict(**AX, range=[0, 110]),
        margin=dict(l=0, r=0, t=20, b=0)))
    st.plotly_chart(fig_all, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  FOOTER CTA
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
