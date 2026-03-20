import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import numpy as np

# ══════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
#  전역 스타일 — 밝고 따뜻한 웜 테마
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Lora:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    color: #1C1917;
}

/* ── 전체 배경 ── */
.stApp { background: #FAFAF8; }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E7E5E0;
}

/* ── 크롬 숨김 ── */
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 2rem; }

/* ══ 워드마크 ══ */
.wordmark {
    padding: 24px 20px 18px;
    border-bottom: 1px solid #F0EDE8;
    margin-bottom: 20px;
}
.wordmark-title {
    font-family: 'Lora', serif;
    font-size: 20px;
    color: #C2793E;
    letter-spacing: -0.01em;
}
.wordmark-sub {
    font-size: 10px; font-weight: 600; color: #A8A29E;
    letter-spacing: 0.1em; text-transform: uppercase; margin-top: 3px;
}

/* ══ 페이지 헤더 ══ */
.page-eyebrow {
    font-size: 10px; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: #C2793E; margin-bottom: 6px;
}
.page-title {
    font-family: 'Lora', serif;
    font-size: 30px; color: #1C1917; line-height: 1.2; margin-bottom: 6px;
}
.page-title em { color: #C2793E; font-style: normal; }
.page-desc { font-size: 13px; color: #78716C; margin-bottom: 24px; }

/* ══ KPI 카드 ══ */
.kpi-row { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.kpi-card {
    flex: 1; min-width: 120px;
    background: #FFFFFF;
    border: 1px solid #E7E5E0;
    border-radius: 14px;
    padding: 16px 18px 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.kpi-card.hl { border-color: #C2793E; background: #FFF7F0; }
.kpi-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.11em;
    text-transform: uppercase; color: #A8A29E; margin-bottom: 8px;
}
.kpi-value { font-family: 'Lora', serif; font-size: 28px; color: #1C1917; line-height: 1; }
.kpi-value.amber { color: #C2793E; }
.kpi-delta { font-size: 11px; font-weight: 500; color: #A8A29E; margin-top: 5px; }
.kpi-delta.up   { color: #16A34A; }
.kpi-delta.down { color: #DC2626; }

/* ══ 위험도 배지 ══ */
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px; border-radius: 100px;
    font-size: 12px; font-weight: 700; letter-spacing: 0.02em;
}
.b-safe    { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.b-ok      { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.b-caution { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }
.b-danger  { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }

/* ══ 섹션 레이블 ══ */
.sec-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    color: #A8A29E; margin-bottom: 14px;
    display: flex; align-items: center; gap: 7px;
}
.sec-label::before {
    content: ''; display: inline-block;
    width: 3px; height: 11px; background: #C2793E; border-radius: 2px;
}

/* ══ 인사이트 ══ */
.insight { border-radius: 10px; padding: 13px 15px; font-size: 13px; line-height: 1.65; }
.i-good  { background: #F0FDF4; border-left: 3px solid #22C55E; color: #14532D; }
.i-warn  { background: #FFF7ED; border-left: 3px solid #F97316; color: #7C2D12; }
.i-neut  { background: #FEFCE8; border-left: 3px solid #EAB308; color: #713F12; }

/* ══ 구분선 ══ */
.hr { border: none; border-top: 1px solid #E7E5E0; margin: 18px 0; }

/* ══ 통계 행 ══ */
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid #F0EDE8; font-size: 13px;
}
.stat-row:last-child { border-bottom: none; }
.stat-key { color: #78716C; }

/* ══ 버튼 ══ */
.stButton > button {
    background: #C2793E !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 10px 22px !important;
    box-shadow: 0 2px 6px rgba(194,121,62,0.3) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ══ 탭 ══ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #F0EDE8; border-radius: 10px;
    padding: 3px; border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; padding: 7px 16px !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #78716C !important; letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #1C1917 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

/* ══ selectbox ══ */
.stSelectbox > div > div {
    background: #FFFFFF !important; border: 1px solid #E7E5E0 !important;
    border-radius: 10px !important; color: #1C1917 !important;
}

/* ══ 지도 iframe ══ */
iframe { border-radius: 12px; border: 1px solid #E7E5E0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  Plotly 기본 레이아웃
# ══════════════════════════════════════════════
BASE = dict(
    font_family="Noto Sans KR, sans-serif",
    font_color="#1C1917",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=28, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1, font_size=11, bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(gridcolor="#F0EDE8", tickfont_size=11, showline=False),
    yaxis=dict(gridcolor="#F0EDE8", tickfont_size=11, showline=False),
)

C_AMBER  = "#C2793E"
C_BLUE   = "#3B82F6"
C_RED    = "#EF4444"
C_GREEN  = "#22C55E"
C_YELLOW = "#EAB308"
C_MUTED  = "#D6D3CE"

# ══════════════════════════════════════════════
#  데이터
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    regions = {
        "연남동": {"score": 71.5, "stores": 20, "open": 4,  "close": 6,  "lat": 37.561, "lng": 126.924},
        "성수동": {"score": 32.1, "stores": 35, "open": 12, "close": 2,  "lat": 37.544, "lng": 127.056},
        "한남동": {"score": 45.8, "stores": 18, "open": 5,  "close": 4,  "lat": 37.535, "lng": 127.001},
        "방배동": {"score": 55.2, "stores": 22, "open": 3,  "close": 5,  "lat": 37.483, "lng": 126.991},
        "망원동": {"score": 28.4, "stores": 25, "open": 8,  "close": 1,  "lat": 37.556, "lng": 126.901},
    }
    rows = []
    for name, d in regions.items():
        s = d["score"]
        if   s >= 65: grade, cls = "고위험", "danger"
        elif s >= 50: grade, cls = "주의",   "caution"
        elif s >= 35: grade, cls = "보통",   "ok"
        else:         grade, cls = "유망",   "safe"
        rows.append({
            **d, "지역": name, "등급": grade, "등급cls": cls,
            "생존율": round(1 - d["close"] / max(d["open"], 1), 2),
        })
    return pd.DataFrame(rows)


@st.cache_data
def load_trend():
    np.random.seed(7)
    trends = {
        "연남동": {"base_o": 8,  "base_c": 5,  "dir": "decline"},
        "성수동": {"base_o": 6,  "base_c": 2,  "dir": "growth"},
        "한남동": {"base_o": 6,  "base_c": 4,  "dir": "stable"},
        "방배동": {"base_o": 5,  "base_c": 4,  "dir": "stable"},
        "망원동": {"base_o": 7,  "base_c": 1,  "dir": "growth"},
    }
    rows = []
    for region, t in trends.items():
        for i, yr in enumerate(range(2019, 2026)):
            if t["dir"] == "growth":
                o = max(1, int(t["base_o"] + i * 1.5 + np.random.randn() * 1.2))
                c = max(0, int(t["base_c"] + i * 0.3 + np.random.randn() * 0.8))
            elif t["dir"] == "decline":
                o = max(1, int(t["base_o"] - i * 0.6 + np.random.randn() * 1.2))
                c = max(0, int(t["base_c"] + i * 0.8 + np.random.randn() * 0.8))
            else:
                o = max(1, int(t["base_o"] + np.random.randn() * 1.5))
                c = max(0, int(t["base_c"] + np.random.randn() * 1.0))
            rows.append({"지역": region, "연도": yr, "개업": o, "폐업": c})
    return pd.DataFrame(rows)


df       = load_data()
trend_df = load_trend()

COLOR_MAP   = {"safe": C_GREEN, "ok": C_YELLOW, "caution": C_AMBER, "danger": C_RED}
BADGE_CLS   = {"safe": "b-safe", "ok": "b-ok", "caution": "b-caution", "danger": "b-danger"}
GRADE_LABEL = {"safe": "유망 ↑", "ok": "보통", "caution": "주의 ↓", "danger": "고위험 ✕"}

# ══════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="wordmark">
        <div class="wordmark-title">🥐 BakeMap</div>
        <div class="wordmark-sub">베이커리 상권 분석</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label" style="padding:0 2px;">분석 지역 선택</div>', unsafe_allow_html=True)
    selected = st.selectbox("지역", df["지역"].tolist(), label_visibility="collapsed")

    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    info = df[df["지역"] == selected].iloc[0]
    cls  = info["등급cls"]

    stat_items = [
        ("SRS 점수",    f"{info['score']:.1f} / 100"),
        ("현재 매장",   f"{info['stores']}개"),
        ("최근 개업",   f"{info['open']}건"),
        ("최근 폐업",   f"{info['close']}건"),
        ("생존율 추정", f"{int(info['생존율']*100)}%"),
    ]
    rows_html = "".join(
        f'<div class="stat-row">'
        f'<span class="stat-key">{k}</span>'
        f'<span style="font-weight:700;color:#1C1917;">{v}</span>'
        f'</div>'
        for k, v in stat_items
    )
    st.markdown(f"""
    <div style="padding:0 2px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:0.11em;text-transform:uppercase;
                    color:#A8A29E;margin-bottom:10px;">선택 지역 요약</div>
        <div style="font-family:'Lora',serif;font-size:20px;color:#1C1917;margin-bottom:8px;">{selected}</div>
        <span class="badge {BADGE_CLS[cls]}">{GRADE_LABEL[cls]}</span>
        <div style="margin-top:14px;">{rows_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#C0B9B3;line-height:1.8;">
    출처: 서울 열린데이터 광장<br>서울시 제과점영업 인허가 정보<br>
    <span style="color:#D6D3CE;">※ 데모 모의 데이터</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  본문 데이터 준비
# ══════════════════════════════════════════════
region_trend = trend_df[trend_df["지역"] == selected].sort_values("연도")
latest = region_trend[region_trend["연도"] == 2025].iloc[0]
prev   = region_trend[region_trend["연도"] == 2024].iloc[0]
open_d  = int(latest["개업"] - prev["개업"])
close_d = int(latest["폐업"] - prev["폐업"])
net     = int(latest["개업"] - latest["폐업"])
srs     = float(info["score"])

# ── 페이지 헤더 ──
st.markdown(f"""
<div class="page-eyebrow">상권 분석 리포트 · 2019–2025</div>
<div class="page-title">{selected} <em>베이커리 시장</em></div>
<div class="page-desc">서울시 제과점영업 인허가 공공데이터 기반 분석</div>
""", unsafe_allow_html=True)

# ── KPI 카드 ──
od_cls  = "up"   if open_d  >= 0 else "down"
cd_cls  = "down" if close_d >  0 else "up"
net_cls = "up"   if net     >= 0 else "down"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card hl">
    <div class="kpi-label">창업 위험도 SRS</div>
    <div class="kpi-value amber">{srs:.1f}<span style="font-size:15px;color:#C2793E;opacity:.6;"> /100</span></div>
    <div style="margin-top:8px;"><span class="badge {BADGE_CLS[cls]}">{GRADE_LABEL[cls]}</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">현재 매장 수</div>
    <div class="kpi-value">{info['stores']}</div>
    <div class="kpi-delta">영업 중인 제과·베이커리</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">최근 개업</div>
    <div class="kpi-value">{int(latest['개업'])}</div>
    <div class="kpi-delta {od_cls}">{'▲' if open_d>=0 else '▼'} {abs(open_d)} 전년 대비</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">최근 폐업</div>
    <div class="kpi-value">{int(latest['폐업'])}</div>
    <div class="kpi-delta {cd_cls}">{'▲' if close_d>=0 else '▼'} {abs(close_d)} 전년 대비</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">순 증감</div>
    <div class="kpi-value">{'+' if net>=0 else ''}{net}</div>
    <div class="kpi-delta {net_cls}">개업 − 폐업</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  탭
# ══════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["  지도 & 분포  ", "  개·폐업 추이  ", "  전체 상권 비교  "])

# ── TAB 1: 지도 ──────────────────────────────
with tab1:
    col_map, col_info = st.columns([3, 2], gap="large")

    with col_map:
        st.markdown('<div class="sec-label">지역별 상권 지도</div>', unsafe_allow_html=True)
        m = folium.Map(location=[37.530, 126.980], zoom_start=12, tiles="cartodbpositron")
        for _, row in df.iterrows():
            is_sel = row["지역"] == selected
            c = COLOR_MAP[row["등급cls"]]
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=row["stores"] * 0.35 + (8 if is_sel else 5),
                color=c, fill=True, fill_color=c,
                fill_opacity=0.85 if is_sel else 0.45,
                weight=3 if is_sel else 1.5,
                tooltip=folium.Tooltip(
                    f"<b>{row['지역']}</b> · SRS {row['score']}점 ({row['등급']})<br>"
                    f"매장 {row['stores']}개 / 개업 {row['open']} / 폐업 {row['close']}",
                    style="font-family:'Noto Sans KR',sans-serif;font-size:12px;"
                ),
            ).add_to(m)
        st_folium(m, width="100%", height=400, key="main_map")

    with col_info:
        st.markdown('<div class="sec-label">SRS 점수 비교</div>', unsafe_allow_html=True)
        df_s = df.sort_values("score")
        bar_colors = [
            COLOR_MAP[r] if n == selected else C_MUTED
            for n, r in zip(df_s["지역"], df_s["등급cls"])
        ]
        fig_srs = go.Figure(go.Bar(
            x=df_s["score"],
            y=df_s["지역"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.1f}" for v in df_s["score"]],
            textposition="outside",
            textfont=dict(size=12, color="#1C1917"),
        ))
        fig_srs.add_vline(
            x=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
            annotation_text="유망", annotation_font_size=10,
            annotation_font_color="rgba(22,163,74,0.9)",
        )
        fig_srs.add_vline(
            x=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
            annotation_text="위험", annotation_font_size=10,
            annotation_font_color="rgba(185,28,28,0.9)",
        )
        fig_srs.update_layout(
            **BASE, height=240,
            xaxis=dict(**BASE["xaxis"], range=[0, 115]),
            margin=dict(l=0, r=36, t=10, b=0),
        )
        st.plotly_chart(fig_srs, use_container_width=True)

        st.markdown('<div class="sec-label">데이터 인사이트</div>', unsafe_allow_html=True)
        recent3  = region_trend[region_trend["연도"] >= 2023]
        close_gt = int((recent3["폐업"] > recent3["개업"]).sum())
        if close_gt >= 2:
            ins_cls = "i-warn"
            ins_txt = f"최근 3년 중 <b>{close_gt}년</b> 연속 폐업 &gt; 개업. 상권 포화 가능성이 있습니다."
        elif srs <= 35:
            ins_cls = "i-good"
            ins_txt = "폐업률이 낮고 개업 증가세가 안정적인 <b>유망 상권</b>입니다."
        else:
            ins_cls = "i-neut"
            ins_txt = "개업과 폐업이 균형을 이루는 <b>안정 국면</b>. 경쟁 강도를 추가 확인하세요."
        st.markdown(f'<div class="insight {ins_cls}">{ins_txt}</div>', unsafe_allow_html=True)

# ── TAB 2: 추이 ──────────────────────────────
with tab2:
    left2, right2 = st.columns([5, 2], gap="large")

    with left2:
        st.markdown('<div class="sec-label">연도별 개·폐업 현황</div>', unsafe_allow_html=True)
        net_series = region_trend["개업"] - region_trend["폐업"]

        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(
            x=region_trend["연도"], y=region_trend["개업"],
            name="개업", marker_color=C_BLUE, opacity=0.85,
        ))
        fig_t.add_trace(go.Bar(
            x=region_trend["연도"], y=-region_trend["폐업"],
            name="폐업", marker_color=C_RED, opacity=0.85,
        ))
        fig_t.add_trace(go.Scatter(
            x=region_trend["연도"], y=net_series,
            mode="lines+markers", name="순증감",
            line=dict(color=C_AMBER, width=2.5),
            marker=dict(size=7, color=C_AMBER,
                        line=dict(color="#FFFFFF", width=2)),
        ))
        fig_t.update_layout(
            **BASE, barmode="overlay", height=320,
            yaxis=dict(**BASE["yaxis"], zeroline=True, zerolinecolor="#E7E5E0"),
            xaxis=dict(**BASE["xaxis"], tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="sec-label" style="margin-top:20px;">누적 순증감</div>', unsafe_allow_html=True)
        rt2 = region_trend.copy()
        rt2["누적"] = (rt2["개업"] - rt2["폐업"]).cumsum()
        lc      = C_GREEN if rt2["누적"].iloc[-1] >= 0 else C_RED
        fill_c  = "rgba(34,197,94,0.08)" if lc == C_GREEN else "rgba(239,68,68,0.08)"

        fig_cum = go.Figure(go.Scatter(
            x=rt2["연도"], y=rt2["누적"],
            fill="tozeroy", fillcolor=fill_c,
            line=dict(color=lc, width=2),
            mode="lines+markers",
            marker=dict(size=6, color=lc,
                        line=dict(color="#FFFFFF", width=2)),
        ))
        fig_cum.update_layout(
            **BASE, height=190,
            yaxis=dict(**BASE["yaxis"], zeroline=True, zerolinecolor="#E7E5E0"),
            xaxis=dict(**BASE["xaxis"], tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig_cum, use_container_width=True)

    with right2:
        st.markdown('<div class="sec-label">기간 요약 (2019–2025)</div>', unsafe_allow_html=True)
        p_open  = int(region_trend["개업"].sum())
        p_close = int(region_trend["폐업"].sum())
        p_net   = p_open - p_close

        stats = [
            ("기간 총 개업",  f"{p_open}건",  ""),
            ("기간 총 폐업",  f"{p_close}건", ""),
            ("기간 순 증감",  f"{'+' if p_net>=0 else ''}{p_net}건", "up" if p_net>=0 else "down"),
            ("폐업률",        f"{round(p_close/max(p_open,1)*100)}%", ""),
            ("생존율 추정",   f"{int(info['생존율']*100)}%", ""),
        ]
        for k, v, sc in stats:
            vc = "#16A34A" if sc=="up" else "#DC2626" if sc=="down" else "#1C1917"
            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-key">{k}</span>'
                f'<span style="color:{vc};font-weight:700;font-size:13px;">{v}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">위험도 게이지</div>', unsafe_allow_html=True)

        gc = COLOR_MAP[cls]
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=srs,
            number={"suffix": "점", "font": {"size": 26, "color": "#1C1917",
                                              "family": "Lora, serif"}},
            gauge={
                "axis": {"range": [0, 100], "tickvals": [], "tickwidth": 0},
                "bar":  {"color": gc, "thickness": 0.22},
                "bgcolor": "#F0EDE8",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  35], "color": "rgba(34,197,94,0.12)"},
                    {"range": [35, 65], "color": "rgba(234,179,8,0.10)"},
                    {"range": [65,100], "color": "rgba(239,68,68,0.10)"},
                ],
            },
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Noto Sans KR, sans-serif",
            height=165, margin=dict(l=10, r=10, t=10, b=0),
        )
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:-10px;">'
            f'<span class="badge {BADGE_CLS[cls]}">{GRADE_LABEL[cls]}</span></div>',
            unsafe_allow_html=True,
        )

# ── TAB 3: 전체 비교 ─────────────────────────
with tab3:
    st.markdown('<div class="sec-label">전체 지역 SRS 종합 비교</div>', unsafe_allow_html=True)

    df_s2 = df.sort_values("score")
    all_colors = [
        COLOR_MAP[r] if n == selected else "#E7E5E0"
        for n, r in zip(df_s2["지역"], df_s2["등급cls"])
    ]
    fig_all = go.Figure(go.Bar(
        x=df_s2["지역"],
        y=df_s2["score"],
        marker_color=all_colors,
        text=[f"{v:.1f}" for v in df_s2["score"]],
        textposition="outside",
        textfont=dict(size=13, color="#1C1917"),
    ))
    fig_all.add_hline(
        y=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
        annotation_text="유망 기준 35점", annotation_font_size=11,
        annotation_font_color="rgba(22,163,74,0.8)",
    )
    fig_all.add_hline(
        y=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
        annotation_text="위험 기준 65점", annotation_font_size=11,
        annotation_font_color="rgba(185,28,28,0.8)",
    )
    fig_all.update_layout(
        **BASE, height=320,
        yaxis=dict(**BASE["yaxis"], range=[0, 110]),
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig_all, use_container_width=True)

    st.markdown('<hr class="hr"><div class="sec-label">상세 데이터 테이블</div>', unsafe_allow_html=True)
    display = df[["지역", "등급", "score", "stores", "open", "close", "생존율"]].copy()
    display.columns = ["지역", "등급", "SRS 점수", "매장 수", "최근 개업", "최근 폐업", "생존율"]
    display["생존율"] = display["생존율"].apply(lambda x: f"{int(x*100)}%")
    display = display.sort_values("SRS 점수")
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SRS 점수": st.column_config.ProgressColumn(
                "SRS 점수", min_value=0, max_value=100, format="%.1f"
            )
        },
    )

# ══════════════════════════════════════════════
#  하단 CTA
# ══════════════════════════════════════════════
st.markdown('<hr class="hr">', unsafe_allow_html=True)
btn_col, txt_col = st.columns([1, 3])
with btn_col:
    if st.button("📄 PDF 리포트 생성", use_container_width=True):
        st.toast("🔒 비즈니스 플랜 구독 후 이용 가능합니다.", icon="📄")
with txt_col:
    st.markdown("""
    <div style="font-size:12px;color:#A8A29E;padding-top:12px;line-height:1.9;">
    상권 요약 · 시계열 차트 · SRS 점수 · 추천 지역이 포함된 PDF 리포트를 생성합니다.<br>
    창업 계획서 · 투자 제안서 · 금융기관 대출 심사 서류에 활용 가능합니다.
    </div>
    """, unsafe_allow_html=True)
