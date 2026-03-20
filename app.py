import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BakeMap · 베이커리 상권 분석",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — 밝은 웜 테마
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=Lora:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    color: #1C1917;
}

/* 전체 배경 */
.stApp { background: #F8F6F2; }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E7E4DF;
}

/* 크롬 숨김 */
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* 워드마크 */
.wm { padding: 22px 20px 16px; border-bottom: 1px solid #F0EDE8; margin-bottom: 18px; }
.wm-title { font-family: 'Lora', serif; font-size: 20px; color: #B8622A; letter-spacing: -0.01em; }
.wm-sub   { font-size: 10px; font-weight: 600; color: #B0A89E; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 3px; }

/* 페이지 헤더 */
.eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #B8622A; margin-bottom: 5px; }
.ptitle  { font-family: 'Lora', serif; font-size: 28px; color: #1C1917; line-height: 1.2; margin-bottom: 4px; }
.ptitle em { color: #B8622A; font-style: normal; }
.pdesc   { font-size: 13px; color: #6B6560; margin-bottom: 22px; }

/* KPI 카드 */
.krow { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.kcard {
    flex: 1; min-width: 110px;
    background: #FFFFFF;
    border: 1px solid #E7E4DF;
    border-radius: 12px;
    padding: 15px 17px 13px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.kcard.hl { border-color: #B8622A; background: #FEF5EE; }
.klabel   { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #A8A29E; margin-bottom: 7px; }
.kval     { font-family: 'Lora', serif; font-size: 26px; color: #1C1917; line-height: 1; }
.kval.amber { color: #B8622A; }
.kdelta   { font-size: 11px; font-weight: 500; color: #A8A29E; margin-top: 4px; }
.kdelta.up   { color: #16A34A; }
.kdelta.down { color: #DC2626; }

/* 배지 */
.bdg { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.bdg-safe    { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.bdg-ok      { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.bdg-caution { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }
.bdg-danger  { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }

/* 섹션 레이블 */
.slabel {
    font-size: 10px; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    color: #A8A29E; margin-bottom: 12px; display: flex; align-items: center; gap: 7px;
}
.slabel::before { content:''; display:inline-block; width:3px; height:10px; background:#B8622A; border-radius:2px; }

/* 인사이트 박스 */
.insight { border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.65; }
.ins-good { background: #F0FDF4; border-left: 3px solid #22C55E; color: #14532D; }
.ins-warn { background: #FFF7ED; border-left: 3px solid #F97316; color: #7C2D12; }
.ins-neut { background: #FEFCE8; border-left: 3px solid #EAB308; color: #713F12; }

/* 구분선 */
.hr { border: none; border-top: 1px solid #E7E4DF; margin: 16px 0; }

/* 통계 행 */
.srow { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid #F0EDE8; font-size:13px; }
.srow:last-child { border-bottom:none; }
.skey { color: #78716C; }

/* 버튼 */
.stButton > button {
    background: #B8622A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 10px 20px !important;
    box-shadow: 0 2px 6px rgba(184,98,42,0.28) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    background: #EDE9E4; border-radius: 10px; padding: 3px; gap: 0; border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; padding: 7px 15px !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #78716C !important; letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #1C1917 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

/* selectbox */
.stSelectbox > div > div {
    background: #FFFFFF !important; border: 1px solid #E7E4DF !important;
    border-radius: 10px !important; color: #1C1917 !important;
}

/* 지도 */
iframe { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Plotly 기본 레이아웃 (라이트)
# ─────────────────────────────────────────────
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
)
AX  = dict(gridcolor="#EDE9E4", tickfont_size=11, showline=False)   # 기본 축

def lay(**kw):
    """BASE에 추가 옵션을 병합해 layout dict 반환 (xaxis/yaxis 중복 없음)"""
    return {**BASE, **kw}

CA = "#B8622A"   # 앰버 (포인트)
CB = "#3B82F6"   # 파랑 (개업)
CR = "#EF4444"   # 빨강 (폐업)
CG = "#22C55E"   # 초록 (유망)
CY = "#EAB308"   # 노랑 (보통)
CM = "#D6D3CE"   # 뮤트 (비선택)

# ─────────────────────────────────────────────
# 데이터
# ─────────────────────────────────────────────
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
        "연남동": {"bo": 8, "bc": 5, "dir": "decline"},
        "성수동": {"bo": 6, "bc": 2, "dir": "growth"},
        "한남동": {"bo": 6, "bc": 4, "dir": "stable"},
        "방배동": {"bo": 5, "bc": 4, "dir": "stable"},
        "망원동": {"bo": 7, "bc": 1, "dir": "growth"},
    }
    rows = []
    for region, t in trends.items():
        for i, yr in enumerate(range(2019, 2026)):
            if t["dir"] == "growth":
                o = max(1, int(t["bo"] + i * 1.5 + np.random.randn() * 1.2))
                c = max(0, int(t["bc"] + i * 0.3 + np.random.randn() * 0.8))
            elif t["dir"] == "decline":
                o = max(1, int(t["bo"] - i * 0.6 + np.random.randn() * 1.2))
                c = max(0, int(t["bc"] + i * 0.8 + np.random.randn() * 0.8))
            else:
                o = max(1, int(t["bo"] + np.random.randn() * 1.5))
                c = max(0, int(t["bc"] + np.random.randn() * 1.0))
            rows.append({"지역": region, "연도": yr, "개업": o, "폐업": c})
    return pd.DataFrame(rows)


df       = load_data()
trend_df = load_trend()

CMAP   = {"safe": CG, "ok": CY, "caution": CA, "danger": CR}
BDGCLS = {"safe": "bdg-safe", "ok": "bdg-ok", "caution": "bdg-caution", "danger": "bdg-danger"}
GLABEL = {"safe": "유망 ↑", "ok": "보통", "caution": "주의 ↓", "danger": "고위험 ✕"}

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="wm">
        <div class="wm-title">🥐 BakeMap</div>
        <div class="wm-sub">베이커리 상권 분석</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slabel" style="padding:0 2px;">분석 지역 선택</div>', unsafe_allow_html=True)
    selected = st.selectbox("지역", df["지역"].tolist(), label_visibility="collapsed")

    info = df[df["지역"] == selected].iloc[0]
    cls  = str(info["등급cls"])
    srs  = float(info["score"])

    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    items_html = "".join(
        f'<div class="srow"><span class="skey">{k}</span>'
        f'<span style="font-weight:700;color:#1C1917;">{v}</span></div>'
        for k, v in [
            ("SRS 점수",    f"{srs:.1f} / 100"),
            ("현재 매장",   f"{int(info['stores'])}개"),
            ("최근 개업",   f"{int(info['open'])}건"),
            ("최근 폐업",   f"{int(info['close'])}건"),
            ("생존율 추정", f"{int(info['생존율'] * 100)}%"),
        ]
    )
    st.markdown(f"""
    <div style="padding:0 2px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                    color:#A8A29E;margin-bottom:9px;">선택 지역 요약</div>
        <div style="font-family:'Lora',serif;font-size:20px;color:#1C1917;margin-bottom:7px;">{selected}</div>
        <span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span>
        <div style="margin-top:13px;">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#C0B9B3;line-height:1.8;">
    출처: 서울 열린데이터 광장<br>서울시 제과점영업 인허가 정보<br>
    <span style="color:#D6D3CE;">※ 데모 모의 데이터</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 본문 데이터
# ─────────────────────────────────────────────
rt = trend_df[trend_df["지역"] == selected].sort_values("연도").reset_index(drop=True)
latest = rt[rt["연도"] == 2025].iloc[0]
prev   = rt[rt["연도"] == 2024].iloc[0]
open_d  = int(latest["개업"] - prev["개업"])
close_d = int(latest["폐업"] - prev["폐업"])
net     = int(latest["개업"] - latest["폐업"])

# 헤더
st.markdown(f"""
<div class="eyebrow">상권 분석 리포트 · 2019–2025</div>
<div class="ptitle">{selected} <em>베이커리 시장</em></div>
<div class="pdesc">서울시 제과점영업 인허가 공공데이터 기반 분석</div>
""", unsafe_allow_html=True)

# KPI 카드
def delta_html(d, reverse=False):
    up = d >= 0 if not reverse else d <= 0
    css = "up" if up else "down"
    arrow = "▲" if d >= 0 else "▼"
    return f'<div class="kdelta {css}">{arrow} {abs(d)} 전년 대비</div>'

net_css = "up" if net >= 0 else "down"

st.markdown(f"""
<div class="krow">
  <div class="kcard hl">
    <div class="klabel">창업 위험도 SRS</div>
    <div class="kval amber">{srs:.1f}<span style="font-size:14px;color:#B8622A;opacity:.55;"> /100</span></div>
    <div style="margin-top:7px;"><span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span></div>
  </div>
  <div class="kcard">
    <div class="klabel">현재 매장 수</div>
    <div class="kval">{int(info['stores'])}</div>
    <div class="kdelta">영업 중인 제과·베이커리</div>
  </div>
  <div class="kcard">
    <div class="klabel">최근 개업</div>
    <div class="kval">{int(latest['개업'])}</div>
    {delta_html(open_d)}
  </div>
  <div class="kcard">
    <div class="klabel">최근 폐업</div>
    <div class="kval">{int(latest['폐업'])}</div>
    {delta_html(close_d, reverse=True)}
  </div>
  <div class="kcard">
    <div class="klabel">순 증감</div>
    <div class="kval">{'+' if net >= 0 else ''}{net}</div>
    <div class="kdelta {net_css}">개업 − 폐업</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 탭
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  지도 & 분포  ", "  개·폐업 추이  ", "  전체 상권 비교  "])

# ── TAB 1 ──
with tab1:
    c_map, c_side = st.columns([3, 2], gap="large")

    with c_map:
        st.markdown('<div class="slabel">지역별 상권 지도</div>', unsafe_allow_html=True)
        m = folium.Map(location=[37.530, 126.980], zoom_start=12, tiles="cartodbpositron")
        for _, row in df.iterrows():
            is_sel = row["지역"] == selected
            c = CMAP[row["등급cls"]]
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=float(row["stores"]) * 0.35 + (8 if is_sel else 5),
                color=c, fill=True, fill_color=c,
                fill_opacity=0.85 if is_sel else 0.45,
                weight=3 if is_sel else 1.5,
                tooltip=folium.Tooltip(
                    f"<b>{row['지역']}</b> · SRS {row['score']}점 ({row['등급']})<br>"
                    f"매장 {row['stores']}개 | 개업 {row['open']} / 폐업 {row['close']}",
                    style="font-family:'Noto Sans KR',sans-serif;font-size:12px;"
                ),
            ).add_to(m)
        st_folium(m, width="100%", height=400, key="map1")

    with c_side:
        st.markdown('<div class="slabel">SRS 점수 비교</div>', unsafe_allow_html=True)
        df_s = df.sort_values("score")
        bar_clrs = [CMAP[r] if n == selected else CM
                    for n, r in zip(df_s["지역"], df_s["등급cls"])]

        fig_srs = go.Figure(go.Bar(
            x=list(df_s["score"]),
            y=list(df_s["지역"]),
            orientation="h",
            marker_color=bar_clrs,
            text=[f"{v:.1f}" for v in df_s["score"]],
            textposition="outside",
            textfont=dict(size=12, color="#1C1917"),
        ))
        fig_srs.add_vline(x=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
                          annotation_text="유망", annotation_font_size=10,
                          annotation_font_color="rgba(22,163,74,0.9)")
        fig_srs.add_vline(x=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                          annotation_text="위험", annotation_font_size=10,
                          annotation_font_color="rgba(185,28,28,0.9)")
        fig_srs.update_layout(**lay(
            height=240,
            xaxis=dict(**AX, range=[0, 115]),
            yaxis=dict(**AX),
            margin=dict(l=0, r=36, t=10, b=0),
        ))
        st.plotly_chart(fig_srs, use_container_width=True)

        st.markdown('<div class="slabel">데이터 인사이트</div>', unsafe_allow_html=True)
        r3 = rt[rt["연도"] >= 2023]
        cgt = int((r3["폐업"] > r3["개업"]).sum())
        if cgt >= 2:
            ic, it = "ins-warn", f"최근 3년 중 <b>{cgt}년</b> 연속 폐업 &gt; 개업. 상권 포화 가능성이 있습니다."
        elif srs <= 35:
            ic, it = "ins-good", "폐업률이 낮고 개업 증가세가 안정적인 <b>유망 상권</b>입니다."
        else:
            ic, it = "ins-neut", "개업·폐업이 균형을 이루는 <b>안정 국면</b>. 경쟁 강도를 추가 확인하세요."
        st.markdown(f'<div class="insight {ic}">{it}</div>', unsafe_allow_html=True)

# ── TAB 2 ──
with tab2:
    l2, r2 = st.columns([5, 2], gap="large")

    with l2:
        st.markdown('<div class="slabel">연도별 개·폐업 현황</div>', unsafe_allow_html=True)
        net_s = rt["개업"] - rt["폐업"]

        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(x=list(rt["연도"]), y=list(rt["개업"]),
                               name="개업", marker_color=CB, opacity=0.85))
        fig_t.add_trace(go.Bar(x=list(rt["연도"]), y=list(-rt["폐업"]),
                               name="폐업", marker_color=CR, opacity=0.85))
        fig_t.add_trace(go.Scatter(
            x=list(rt["연도"]), y=list(net_s),
            mode="lines+markers", name="순증감",
            line=dict(color=CA, width=2.5),
            marker=dict(size=7, color=CA, line=dict(color="#FFFFFF", width=2)),
        ))
        fig_t.update_layout(**lay(
            barmode="overlay", height=310,
            xaxis=dict(**AX, tickmode="linear", dtick=1),
            yaxis=dict(**AX, zeroline=True, zerolinecolor="#E7E4DF"),
        ))
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="slabel" style="margin-top:18px;">누적 순증감</div>', unsafe_allow_html=True)
        rt2 = rt.copy()
        rt2["누적"] = (rt2["개업"] - rt2["폐업"]).cumsum()
        lc = CG if float(rt2["누적"].iloc[-1]) >= 0 else CR
        fc = "rgba(34,197,94,0.08)" if lc == CG else "rgba(239,68,68,0.08)"

        fig_c = go.Figure(go.Scatter(
            x=list(rt2["연도"]), y=list(rt2["누적"]),
            fill="tozeroy", fillcolor=fc,
            line=dict(color=lc, width=2), mode="lines+markers",
            marker=dict(size=6, color=lc, line=dict(color="#FFFFFF", width=2)),
        ))
        fig_c.update_layout(**lay(
            height=185,
            xaxis=dict(**AX, tickmode="linear", dtick=1),
            yaxis=dict(**AX, zeroline=True, zerolinecolor="#E7E4DF"),
        ))
        st.plotly_chart(fig_c, use_container_width=True)

    with r2:
        st.markdown('<div class="slabel">기간 요약</div>', unsafe_allow_html=True)
        po = int(rt["개업"].sum())
        pc = int(rt["폐업"].sum())
        pn = po - pc
        for k, v, sc in [
            ("기간 총 개업",  f"{po}건",  ""),
            ("기간 총 폐업",  f"{pc}건",  ""),
            ("순 증감",       f"{'+' if pn>=0 else ''}{pn}건", "up" if pn>=0 else "down"),
            ("폐업률",        f"{round(pc/max(po,1)*100)}%",   ""),
            ("생존율 추정",   f"{int(info['생존율']*100)}%",    ""),
        ]:
            vc = "#16A34A" if sc=="up" else "#DC2626" if sc=="down" else "#1C1917"
            st.markdown(
                f'<div class="srow"><span class="skey">{k}</span>'
                f'<span style="color:{vc};font-weight:700;font-size:13px;">{v}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="slabel">위험도 게이지</div>', unsafe_allow_html=True)
        gc = CMAP[cls]
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=srs,
            number={"suffix": "점", "font": {"size": 26, "color": "#1C1917",
                                              "family": "Lora, serif"}},
            gauge={
                "axis": {"range": [0, 100], "tickvals": [], "tickwidth": 0},
                "bar":  {"color": gc, "thickness": 0.22},
                "bgcolor": "#EDE9E4",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  35], "color": "rgba(34,197,94,0.12)"},
                    {"range": [35, 65], "color": "rgba(234,179,8,0.10)"},
                    {"range": [65,100], "color": "rgba(239,68,68,0.10)"},
                ],
            },
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                            font_family="Noto Sans KR, sans-serif",
                            height=160, margin=dict(l=10, r=10, t=10, b=0))
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:-8px;">'
            f'<span class="bdg {BDGCLS[cls]}">{GLABEL[cls]}</span></div>',
            unsafe_allow_html=True,
        )

# ── TAB 3 ──
with tab3:
    st.markdown('<div class="slabel">전체 지역 SRS 종합 비교</div>', unsafe_allow_html=True)
    df_s2 = df.sort_values("score")
    all_clrs = [CMAP[r] if n == selected else "#E7E4DF"
                for n, r in zip(df_s2["지역"], df_s2["등급cls"])]

    fig_all = go.Figure(go.Bar(
        x=list(df_s2["지역"]),
        y=list(df_s2["score"]),
        marker_color=all_clrs,
        text=[f"{v:.1f}" for v in df_s2["score"]],
        textposition="outside",
        textfont=dict(size=13, color="#1C1917"),
    ))
    fig_all.add_hline(y=35, line_dash="dot", line_color="rgba(34,197,94,0.5)",
                      annotation_text="유망 기준 35점", annotation_font_size=11,
                      annotation_font_color="rgba(22,163,74,0.8)")
    fig_all.add_hline(y=65, line_dash="dot", line_color="rgba(239,68,68,0.5)",
                      annotation_text="위험 기준 65점", annotation_font_size=11,
                      annotation_font_color="rgba(185,28,28,0.8)")
    fig_all.update_layout(**lay(
        height=310,
        xaxis=dict(**AX),
        yaxis=dict(**AX, range=[0, 110]),
        margin=dict(l=0, r=0, t=20, b=0),
    ))
    st.plotly_chart(fig_all, use_container_width=True)

    st.markdown('<hr class="hr"><div class="slabel">상세 데이터 테이블</div>', unsafe_allow_html=True)
    disp = df[["지역", "등급", "score", "stores", "open", "close", "생존율"]].copy()
    disp.columns = ["지역", "등급", "SRS 점수", "매장 수", "최근 개업", "최근 폐업", "생존율"]
    disp["생존율"] = disp["생존율"].apply(lambda x: f"{int(x*100)}%")
    disp = disp.sort_values("SRS 점수")
    st.dataframe(
        disp, use_container_width=True, hide_index=True,
        column_config={
            "SRS 점수": st.column_config.ProgressColumn(
                "SRS 점수", min_value=0, max_value=100, format="%.1f"
            )
        },
    )

# ─────────────────────────────────────────────
# 하단 CTA
# ─────────────────────────────────────────────
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
