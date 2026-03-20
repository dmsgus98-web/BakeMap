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
#  전역 스타일
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

/* ── 기본 리셋 ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    color: #E8E4DC;
}

/* ── 배경 ── */
.stApp {
    background: #0D1117;
    background-image:
        radial-gradient(ellipse 80% 50% at 10% 0%, rgba(212,175,55,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(74,144,226,0.05) 0%, transparent 60%);
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #0A0E13 !important;
    border-right: 1px solid rgba(212,175,55,0.12);
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── 헤더/푸터 숨김 ── */
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.3); border-radius: 2px; }

/* ══ 컴포넌트 ══ */

/* 워드마크 */
.wordmark {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 24px;
}
.wordmark-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #D4AF37;
    letter-spacing: 0.02em;
    line-height: 1;
}
.wordmark-sub {
    font-size: 10px;
    font-weight: 500;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* 섹션 레이블 */
.sidebar-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
    padding: 0 24px;
    margin-bottom: 8px;
}

/* 페이지 헤더 */
.page-header {
    margin-bottom: 28px;
}
.page-eyebrow {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #D4AF37;
    margin-bottom: 8px;
}
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 36px;
    color: #F0EAD6;
    line-height: 1.15;
    letter-spacing: -0.01em;
}
.page-title span {
    color: #D4AF37;
}
.page-desc {
    font-size: 13px;
    color: rgba(255,255,255,0.38);
    margin-top: 8px;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* KPI 카드 */
.kpi-grid { display: flex; gap: 12px; margin-bottom: 20px; }
.kpi-card {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #D4AF37, transparent);
    opacity: 0;
    transition: opacity 0.2s;
}
.kpi-card:hover { border-color: rgba(212,175,55,0.2); }
.kpi-card:hover::before { opacity: 1; }
.kpi-card.accent {
    background: rgba(212,175,55,0.07);
    border-color: rgba(212,175,55,0.2);
}
.kpi-card.accent::before { opacity: 1; }

.kpi-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 30px;
    color: #F0EAD6;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-value.gold { color: #D4AF37; }
.kpi-delta {
    font-size: 11px;
    font-weight: 500;
    margin-top: 6px;
    color: rgba(255,255,255,0.3);
}
.kpi-delta.up   { color: #4ADE80; }
.kpi-delta.down { color: #F87171; }

/* 위험도 배지 */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.risk-safe    { background: rgba(74,222,128,0.12);  color: #4ADE80; border: 1px solid rgba(74,222,128,0.2); }
.risk-ok      { background: rgba(250,204,21,0.10);  color: #FACC15; border: 1px solid rgba(250,204,21,0.2); }
.risk-caution { background: rgba(251,146,60,0.10);  color: #FB923C; border: 1px solid rgba(251,146,60,0.2); }
.risk-danger  { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.2); }

/* 카드 래퍼 */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 14px;
}
.card-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-title::before {
    content: '';
    display: inline-block;
    width: 3px; height: 12px;
    background: #D4AF37;
    border-radius: 2px;
}

/* 구분선 */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 20px 0;
}

/* 지역 행 */
.region-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    cursor: pointer;
    transition: background 0.15s;
}
.region-row:last-child { border-bottom: none; }
.region-name { font-size: 14px; font-weight: 600; color: #E8E4DC; }
.region-meta { font-size: 12px; color: rgba(255,255,255,0.35); margin-top: 2px; }

/* 인사이트 박스 */
.insight {
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.65;
    font-weight: 400;
}
.insight-warn   { background: rgba(251,146,60,0.08); border-left: 3px solid #FB923C; color: #FED7AA; }
.insight-good   { background: rgba(74,222,128,0.08); border-left: 3px solid #4ADE80; color: #BBF7D0; }
.insight-neutral{ background: rgba(250,204,21,0.07); border-left: 3px solid #FACC15; color: #FEF08A; }

/* 데이터 테이블 */
.stDataFrame { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; }

/* 버튼 */
.stButton > button {
    background: #D4AF37 !important;
    color: #0D1117 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    padding: 10px 24px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8E4DC !important;
}

/* Folium 지도 테두리 */
iframe { border-radius: 14px; }

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: rgba(255,255,255,0.45) !important;
    letter-spacing: 0.03em !important;
}
.stTabs [aria-selected="true"] {
    background: #D4AF37 !important;
    color: #0D1117 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  Plotly 다크 테마 기본값
# ══════════════════════════════════════════════
BASE_LAYOUT = dict(
    font_family="Noto Sans KR, sans-serif",
    font_color="#E8E4DC",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=28, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font_size=11, bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont_size=11, showline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont_size=11, showline=False),
)
C_GOLD  = "#D4AF37"
C_BLUE  = "#4A90E2"
C_GREEN = "#4ADE80"
C_RED   = "#F87171"
C_DIM   = "rgba(255,255,255,0.12)"

# ══════════════════════════════════════════════
#  데이터
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    regions = {
        "연남동":  {"score": 71.5, "stores": 20, "open": 4,  "close": 6,  "lat": 37.561, "lng": 126.924},
        "성수동":  {"score": 32.1, "stores": 35, "open": 12, "close": 2,  "lat": 37.544, "lng": 127.056},
        "한남동":  {"score": 45.8, "stores": 18, "open": 5,  "close": 4,  "lat": 37.535, "lng": 127.001},
        "방배동":  {"score": 55.2, "stores": 22, "open": 3,  "close": 5,  "lat": 37.483, "lng": 126.991},
        "망원동":  {"score": 28.4, "stores": 25, "open": 8,  "close": 1,  "lat": 37.556, "lng": 126.901},
    }
    rows = []
    for name, d in regions.items():
        s = d["score"]
        if s >= 65:   grade, cls = "고위험", "danger"
        elif s >= 50: grade, cls = "주의",   "caution"
        elif s >= 35: grade, cls = "보통",   "ok"
        else:         grade, cls = "유망",   "safe"
        rows.append({**d, "지역": name, "등급": grade, "등급cls": cls,
                     "생존율": round(1 - d["close"] / max(d["open"], 1), 2)})
    return pd.DataFrame(rows)

@st.cache_data
def load_trend():
    np.random.seed(7)
    years = list(range(2019, 2026))
    trends = {
        "연남동":  {"base_o": 8,  "base_c": 5,  "dir": "decline"},
        "성수동":  {"base_o": 6,  "base_c": 2,  "dir": "growth"},
        "한남동":  {"base_o": 6,  "base_c": 4,  "dir": "stable"},
        "방배동":  {"base_o": 5,  "base_c": 4,  "dir": "stable"},
        "망원동":  {"base_o": 7,  "base_c": 1,  "dir": "growth"},
    }
    rows = []
    for region, t in trends.items():
        for i, yr in enumerate(years):
            if t["dir"] == "growth":
                o = max(1, int(t["base_o"] + i*1.5 + np.random.randn()*1.2))
                c = max(0, int(t["base_c"] + i*0.3 + np.random.randn()*0.8))
            elif t["dir"] == "decline":
                o = max(1, int(t["base_o"] - i*0.6 + np.random.randn()*1.2))
                c = max(0, int(t["base_c"] + i*0.8 + np.random.randn()*0.8))
            else:
                o = max(1, int(t["base_o"] + np.random.randn()*1.5))
                c = max(0, int(t["base_c"] + np.random.randn()*1.0))
            rows.append({"지역": region, "연도": yr, "개업": o, "폐업": c})
    return pd.DataFrame(rows)

df = load_data()
trend_df = load_trend()

# ══════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="wordmark">
        <div class="wordmark-title">🥐 BakeMap</div>
        <div class="wordmark-sub">베이커리 상권 분석 플랫폼</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">분석 지역</div>', unsafe_allow_html=True)
    selected = st.selectbox("지역 선택", df["지역"].tolist(), label_visibility="collapsed")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    info = df[df["지역"] == selected].iloc[0]
    cls  = info["등급cls"]
    badge_map = {"safe": "risk-safe", "ok": "risk-ok", "caution": "risk-caution", "danger": "risk-danger"}
    grade_map = {"safe": "유망 ↑", "ok": "보통", "caution": "주의 ↓", "danger": "고위험 ✕"}

    st.markdown(f"""
    <div style="padding: 0 4px;">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.13em;text-transform:uppercase;
                    color:rgba(255,255,255,0.28);margin-bottom:12px;">선택 지역 요약</div>
        <div style="font-size:22px;font-family:'DM Serif Display',serif;color:#F0EAD6;margin-bottom:10px;">
            {selected}
        </div>
        <span class="risk-badge {badge_map[cls]}">{grade_map[cls]}</span>
        <div style="margin-top:16px;display:grid;gap:10px;">
            {"".join([
                f'<div style="display:flex;justify-content:space-between;font-size:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                f'<span style="color:rgba(255,255,255,0.35);">{k}</span>'
                f'<span style="color:#E8E4DC;font-weight:600;">{v}</span></div>'
                for k, v in [
                    ("창업 위험도 (SRS)", f"{info['score']:.1f}점"),
                    ("현재 매장 수", f"{info['stores']}개"),
                    ("최근 개업", f"{info['open']}건"),
                    ("최근 폐업", f"{info['close']}건"),
                    ("생존율 추정", f"{int(info['생존율']*100)}%"),
                ]
            ])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;color:rgba(255,255,255,0.2);line-height:1.8;padding:0 4px;">
    데이터: 서울 열린데이터 광장<br>
    서울시 제과점영업 인허가 정보<br>
    ※ 데모 모의 데이터
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  메인 콘텐츠
# ══════════════════════════════════════════════
region_trend = trend_df[trend_df["지역"] == selected].sort_values("연도")
latest = region_trend[region_trend["연도"] == 2025].iloc[0]
prev   = region_trend[region_trend["연도"] == 2024].iloc[0]
open_delta  = int(latest["개업"] - prev["개업"])
close_delta = int(latest["폐업"] - prev["폐업"])
net = int(latest["개업"] - latest["폐업"])

# 헤더
st.markdown(f"""
<div class="page-header">
    <div class="page-eyebrow">상권 분석 리포트</div>
    <div class="page-title">{selected} <span>베이커리 시장</span></div>
    <div class="page-desc">서울시 제과점영업 인허가 공공데이터 기반 · 2019 – 2025</div>
</div>
""", unsafe_allow_html=True)

# ── KPI 카드 ──
d_open  = f"{'▲' if open_delta >= 0 else '▼'} {abs(open_delta)} 전년 대비"
d_close = f"{'▲' if close_delta >= 0 else '▼'} {abs(close_delta)} 전년 대비"
d_net_cls = "up" if net >= 0 else "down"

srs = info["score"]
srs_cls_map = {"safe": "risk-safe", "ok": "risk-ok", "caution": "risk-caution", "danger": "risk-danger"}
srs_badge = f'<span class="risk-badge {srs_cls_map[cls]}">{grade_map[cls]}</span>'

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card accent">
        <div class="kpi-label">창업 위험도 SRS</div>
        <div class="kpi-value gold">{srs:.1f}<span style="font-size:16px;font-weight:400;color:rgba(212,175,55,0.6);">/100</span></div>
        <div style="margin-top:8px;">{srs_badge}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">현재 매장 수</div>
        <div class="kpi-value">{info['stores']}</div>
        <div class="kpi-delta">영업 중인 제과·베이커리</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">최근 개업</div>
        <div class="kpi-value">{int(latest['개업'])}</div>
        <div class="kpi-delta {'up' if open_delta >= 0 else 'down'}">{d_open}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">최근 폐업</div>
        <div class="kpi-value">{int(latest['폐업'])}</div>
        <div class="kpi-delta {'down' if close_delta > 0 else 'up'}">{d_close}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">순 증감</div>
        <div class="kpi-value {'gold' if net > 0 else ''}">{'+' if net >= 0 else ''}{net}</div>
        <div class="kpi-delta {d_net_cls}">개업 − 폐업</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 탭 ──
tab1, tab2, tab3 = st.tabs(["  지도 & 분포  ", "  개·폐업 추이  ", "  전체 상권 비교  "])

# ══ TAB 1: 지도 ══
with tab1:
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="card-title">지역별 상권 지도</div>', unsafe_allow_html=True)
        m = folium.Map(
            location=[37.535, 126.98],
            zoom_start=12,
            tiles="CartoDB dark_matter",
        )
        color_map = {"safe": "#4ADE80", "ok": "#FACC15", "caution": "#FB923C", "danger": "#F87171"}
        for _, row in df.iterrows():
            is_selected = row["지역"] == selected
            c = color_map[row["등급cls"]]
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=row["stores"] * 0.35 + (6 if is_selected else 4),
                color=c,
                fill=True,
                fill_color=c,
                fill_opacity=0.85 if is_selected else 0.5,
                weight=3 if is_selected else 1,
                tooltip=folium.Tooltip(
                    f"<b style='font-size:14px'>{row['지역']}</b><br>"
                    f"SRS: {row['score']}점 &nbsp;|&nbsp; {row['등급']}<br>"
                    f"매장 {row['stores']}개 · 개업 {row['open']} / 폐업 {row['close']}",
                    style="font-family:'Noto Sans KR',sans-serif;font-size:13px;"
                ),
            ).add_to(m)

            if is_selected:
                folium.Marker(
                    location=[row["lat"] + 0.003, row["lng"]],
                    icon=folium.DivIcon(
                        html=f'<div style="font-family:Noto Sans KR,sans-serif;font-size:12px;font-weight:700;color:{c};white-space:nowrap;text-shadow:0 1px 4px rgba(0,0,0,0.8);">{row["지역"]}</div>',
                        icon_size=(80, 20), icon_anchor=(40, 0),
                    )
                ).add_to(m)

        st_folium(m, width="100%", height=420, key="map_v2")

    with right:
        st.markdown('<div class="card-title">SRS 점수 분포</div>', unsafe_allow_html=True)

        df_sorted = df.sort_values("score")
        bar_colors = [color_map[c] + "CC" if r != selected else color_map[c] for r, c in zip(df_sorted["지역"], df_sorted["등급cls"])]

        fig_bar = go.Figure(go.Bar(
            x=df_sorted["score"],
            y=df_sorted["지역"],
            orientation="h",
            marker_color=bar_colors,
            marker_cornerradius=6,
            text=[f"{s:.1f}" for s in df_sorted["score"]],
            textposition="outside",
            textfont=dict(size=12, color="#E8E4DC"),
        ))
        fig_bar.add_vline(x=35, line_dash="dot", line_color="rgba(74,222,128,0.4)",
                          annotation_text="유망", annotation_font_color="rgba(74,222,128,0.6)", annotation_font_size=10)
        fig_bar.add_vline(x=65, line_dash="dot", line_color="rgba(248,113,113,0.4)",
                          annotation_text="위험", annotation_font_color="rgba(248,113,113,0.6)", annotation_font_size=10)
        fig_bar.update_layout(**BASE_LAYOUT, height=260,
                              xaxis=dict(**BASE_LAYOUT["xaxis"], range=[0, 110]),
                              margin=dict(l=0, r=40, t=10, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

        # 인사이트
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">인사이트</div>', unsafe_allow_html=True)
        recent = region_trend[region_trend["연도"] >= 2023]
        close_gt = (recent["폐업"] > recent["개업"]).sum()
        if close_gt >= 2:
            ins = ("warn", f"최근 3년 중 <b>{close_gt}년</b> 연속 폐업이 개업을 초과했습니다. 상권 포화 또는 수요 위축 신호일 수 있어 진입 전 추가 검토가 필요합니다.")
        elif srs <= 35:
            ins = ("good", "개업 증가세가 안정적이고 폐업률이 낮은 <b>유망 상권</b>입니다. 데이터상 창업 리스크가 상대적으로 낮게 측정되었습니다.")
        else:
            ins = ("neutral", "개업과 폐업이 균형을 이루는 <b>안정 국면</b>입니다. 경쟁 강도와 임대료 추이를 추가로 확인하세요.")
        st.markdown(f'<div class="insight insight-{ins[0]}">{ins[1]}</div>', unsafe_allow_html=True)

# ══ TAB 2: 추이 ══
with tab2:
    c_left, c_right = st.columns([5, 2], gap="large")

    with c_left:
        st.markdown('<div class="card-title">연도별 개·폐업 현황</div>', unsafe_allow_html=True)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=region_trend["연도"], y=region_trend["개업"],
            name="개업", marker_color=C_BLUE, marker_cornerradius=4, opacity=0.9,
        ))
        fig_trend.add_trace(go.Bar(
            x=region_trend["연도"], y=-region_trend["폐업"],
            name="폐업", marker_color=C_RED, marker_cornerradius=4, opacity=0.9,
        ))
        net_series = region_trend["개업"] - region_trend["폐업"]
        fig_trend.add_trace(go.Scatter(
            x=region_trend["연도"], y=net_series,
            mode="lines+markers", name="순증감",
            line=dict(color=C_GOLD, width=2.5),
            marker=dict(size=7, color=C_GOLD, line=dict(color="#0D1117", width=2)),
        ))
        fig_trend.update_layout(
            **BASE_LAYOUT, barmode="overlay", height=320,
            yaxis=dict(**BASE_LAYOUT["yaxis"], zeroline=True, zerolinecolor="rgba(255,255,255,0.12)"),
            xaxis=dict(**BASE_LAYOUT["xaxis"], tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # 누적 라인
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">누적 순증감</div>', unsafe_allow_html=True)

        region_trend2 = region_trend.copy()
        region_trend2["누적"] = (region_trend2["개업"] - region_trend2["폐업"]).cumsum()
        line_color = C_GREEN if region_trend2["누적"].iloc[-1] >= 0 else C_RED

        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=region_trend2["연도"], y=region_trend2["누적"],
            fill="tozeroy",
            fillcolor=line_color.replace(")", ",0.10)").replace("rgb", "rgba") if "rgb" in line_color else line_color + "1A",
            line=dict(color=line_color, width=2),
            mode="lines+markers",
            marker=dict(size=6, color=line_color, line=dict(color="#0D1117", width=2)),
        ))
        fig_cum.update_layout(
            **BASE_LAYOUT, height=180,
            yaxis=dict(**BASE_LAYOUT["yaxis"], zeroline=True, zerolinecolor="rgba(255,255,255,0.12)"),
            xaxis=dict(**BASE_LAYOUT["xaxis"], tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig_cum, use_container_width=True)

    with c_right:
        st.markdown('<div class="card-title">기간 요약</div>', unsafe_allow_html=True)
        period_open  = int(region_trend["개업"].sum())
        period_close = int(region_trend["폐업"].sum())
        period_net   = period_open - period_close
        survival_est = round(1 - period_close / max(period_open, 1), 2)

        stats = [
            ("기간 총 개업", f"{period_open}건", ""),
            ("기간 총 폐업", f"{period_close}건", ""),
            ("기간 순 증감", f"{'+'if period_net>=0 else ''}{period_net}건", "up" if period_net >= 0 else "down"),
            ("폐업률", f"{round(period_close/max(period_open,1)*100)}%", ""),
            ("생존율 추정", f"{int(survival_est*100)}%", ""),
        ]
        for label, val, c2 in stats:
            color = f"color:{'#4ADE80' if c2=='up' else '#F87171' if c2=='down' else '#E8E4DC'};font-weight:700;"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;">
                <span style="color:rgba(255,255,255,0.38);">{label}</span>
                <span style="{color}">{val}</span>
            </div>
            """, unsafe_allow_html=True)

        # 미니 게이지
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">위험도 게이지</div>', unsafe_allow_html=True)
        gauge_c = {"safe": C_GREEN, "ok": "#FACC15", "caution": "#FB923C", "danger": C_RED}[cls]
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=srs,
            number={"suffix": "점", "font": {"size": 26, "color": "#F0EAD6", "family": "DM Serif Display"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "transparent", "tickvals": []},
                "bar": {"color": gauge_c, "thickness": 0.22},
                "bgcolor": "rgba(255,255,255,0.05)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  35], "color": "rgba(74,222,128,0.08)"},
                    {"range": [35, 65], "color": "rgba(250,204,21,0.06)"},
                    {"range": [65,100], "color": "rgba(248,113,113,0.08)"},
                ],
            },
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Noto Sans KR",
                            height=160, margin=dict(l=10, r=10, t=10, b=0))
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:-8px;">'
            f'<span class="risk-badge {srs_cls_map[cls]}">{grade_map[cls]}</span></div>',
            unsafe_allow_html=True
        )

# ══ TAB 3: 전체 비교 ══
with tab3:
    st.markdown('<div class="card-title">전체 지역 SRS 종합 비교</div>', unsafe_allow_html=True)

    df_sorted2 = df.sort_values("score")
    fig_all = go.Figure()
    for _, row in df_sorted2.iterrows():
        is_sel = row["지역"] == selected
        c = color_map[row["등급cls"]]
        fig_all.add_trace(go.Bar(
            x=[row["지역"]], y=[row["score"]],
            name=row["지역"],
            marker_color=c if is_sel else C_DIM,
            marker_cornerradius=8,
            text=[f"{row['score']:.1f}"],
            textposition="outside",
            textfont=dict(size=12, color=c if is_sel else "rgba(255,255,255,0.4)"),
            showlegend=False,
        ))

    fig_all.add_hline(y=35, line_dash="dot", line_color="rgba(74,222,128,0.35)",
                      annotation_text="유망 기준 (35점)", annotation_font_size=11,
                      annotation_font_color="rgba(74,222,128,0.6)")
    fig_all.add_hline(y=65, line_dash="dot", line_color="rgba(248,113,113,0.35)",
                      annotation_text="위험 기준 (65점)", annotation_font_size=11,
                      annotation_font_color="rgba(248,113,113,0.6)")
    fig_all.update_layout(
        **BASE_LAYOUT, height=340,
        yaxis=dict(**BASE_LAYOUT["yaxis"], range=[0, 120]),
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig_all, use_container_width=True)

    # 테이블
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">상세 데이터 테이블</div>', unsafe_allow_html=True)
    display_df = df[["지역", "등급", "score", "stores", "open", "close", "생존율"]].copy()
    display_df.columns = ["지역", "등급", "SRS 점수", "매장 수", "최근 개업", "최근 폐업", "생존율"]
    display_df["생존율"] = display_df["생존율"].apply(lambda x: f"{int(x*100)}%")
    display_df = display_df.sort_values("SRS 점수")
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SRS 점수": st.column_config.ProgressColumn(
                "SRS 점수", min_value=0, max_value=100, format="%.1f"
            ),
        },
    )

# ══════════════════════════════════════════════
#  하단 CTA
# ══════════════════════════════════════════════
st.markdown('<hr class="divider">', unsafe_allow_html=True)
cta_l, cta_r = st.columns([1, 3])
with cta_l:
    if st.button("📄 PDF 리포트 생성", use_container_width=True):
        st.toast("📄 리포트 생성은 비즈니스 플랜 구독 후 이용 가능합니다.", icon="🔒")
with cta_r:
    st.markdown("""
    <div style="font-size:12px;color:rgba(255,255,255,0.28);padding-top:12px;line-height:1.8;">
    상권 요약 · 시계열 차트 · SRS 점수 · 추천 지역이 포함된 PDF 리포트를 생성합니다.<br>
    창업 계획서, 투자 제안서, 금융기관 대출 심사 서류에 활용 가능합니다.
    </div>
    """, unsafe_allow_html=True)
