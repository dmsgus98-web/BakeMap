import streamlit as st
import pandas as pd
import plotly.express as px
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
# 전역 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── 폰트 ── */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}

/* ── 전체 배경 ── */
.stApp { background-color: #F9F7F4; }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #ECECEA;
}

/* ── 헤더 숨김 ── */
#MainMenu, header, footer { visibility: hidden; }

/* ── KPI 카드 ── */
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid #ECECEA;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: #9B9B8F;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #1A1A18;
    line-height: 1.2;
}
.kpi-delta {
    font-size: 12px;
    font-weight: 500;
    color: #9B9B8F;
}
.kpi-delta.up   { color: #2E9E6B; }
.kpi-delta.down { color: #D94F3D; }

/* ── 위험도 배지 ── */
.srs-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.srs-safe   { background:#EAF7F0; color:#1E7A50; }
.srs-caution{ background:#FFF4E0; color:#A06000; }
.srs-danger { background:#FEECEB; color:#B83228; }

/* ── 섹션 구분선 ── */
.section-header {
    font-size: 16px;
    font-weight: 700;
    color: #1A1A18;
    padding-bottom: 8px;
    border-bottom: 2px solid #1A1A18;
    margin-bottom: 16px;
}

/* ── 인사이트 박스 ── */
.insight-box {
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.6;
}
.insight-good { background:#EAF7F0; color:#1E5C3A; border-left: 4px solid #2E9E6B; }
.insight-warn { background:#FFF4E0; color:#7A4A00; border-left: 4px solid #F0A500; }
.insight-bad  { background:#FEECEB; color:#8C2218; border-left: 4px solid #D94F3D; }

/* ── 추천 지역 카드 ── */
.rec-card {
    background:#FFFFFF;
    border-radius: 12px;
    padding: 14px 18px;
    border: 1px solid #ECECEA;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.rec-name  { font-size: 15px; font-weight: 600; color: #1A1A18; }
.rec-score { font-size: 14px; font-weight: 700; color: #2E9E6B; }

/* ── 플로팅 타이틀 ── */
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #1A1A18;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 14px;
    color: #9B9B8F;
    margin-bottom: 24px;
}

/* ── 탭 스타일 ── */
button[data-baseweb="tab"] {
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* ── 차트 컨테이너 ── */
.chart-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 4px;
    border: 1px solid #ECECEA;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Plotly 공통 테마
# ─────────────────────────────────────────────
CHART_LAYOUT = dict(
    font_family="Pretendard, Apple SD Gothic Neo, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font_size=12,
    ),
)
COLOR_OPEN  = "#3B82F6"   # 개업 – 파랑
COLOR_CLOSE = "#EF4444"   # 폐업 – 빨강
COLOR_SAFE  = "#2E9E6B"
COLOR_WARN  = "#F0A500"
COLOR_DANGER = "#D94F3D"

# ─────────────────────────────────────────────
# 데이터 (Mock – 서울시 제과점 인허가 구조 반영)
# ─────────────────────────────────────────────
DISTRICTS = {
    "마포구": {"동": ["연남동", "합정동", "망원동", "서교동", "성산동"], "면적": 23.8},
    "서초구": {"동": ["방배동", "반포동", "서초동", "양재동"], "면적": 46.9},
    "강남구": {"동": ["논현동", "역삼동", "청담동", "압구정동"], "면적": 39.5},
    "성동구": {"동": ["성수동", "왕십리동", "금호동", "행당동"], "면적": 16.8},
    "은평구": {"동": ["신사동", "불광동", "응암동", "연신내동"], "면적": 29.7},
    "송파구": {"동": ["잠실동", "석촌동", "방이동", "오금동"], "면적": 33.9},
}

RECOMMENDATIONS = {
    "마포구 연남동": [("마포구 성산동", 38, "+2.1%"), ("은평구 신사동", 41, "+1.8%"), ("성동구 성수동", 32, "+3.4%")],
    "마포구 합정동": [("서초구 방배동", 44, "+1.2%"), ("성동구 성수동", 32, "+3.4%"), ("은평구 불광동", 47, "+0.9%")],
    "성동구 성수동": [("마포구 서교동", 35, "+2.7%"), ("강남구 역삼동", 42, "+1.5%"), ("송파구 석촌동", 48, "+0.6%")],
}

@st.cache_data
def load_data():
    np.random.seed(42)
    rows = []
    for dist, meta in DISTRICTS.items():
        for dong in meta["동"]:
            base_open  = np.random.randint(6, 18)
            base_close = np.random.randint(3, 12)
            trend = np.random.choice(["growth", "stable", "decline"])
            for yr in range(2019, 2026):
                t = yr - 2019
                if trend == "growth":
                    opens  = max(1, int(base_open  + t * 1.4 + np.random.randn()*1.5))
                    closes = max(0, int(base_close + t * 0.4 + np.random.randn()*1.2))
                elif trend == "decline":
                    opens  = max(1, int(base_open  - t * 0.8 + np.random.randn()*1.5))
                    closes = max(0, int(base_close + t * 1.1 + np.random.randn()*1.2))
                else:
                    opens  = max(1, int(base_open  + np.random.randn()*2))
                    closes = max(0, int(base_close + np.random.randn()*1.5))
                rows.append({
                    "자치구": dist, "행정동": dong, "연도": yr,
                    "개업수": opens, "폐업수": closes,
                    "현재매장수": np.random.randint(30, 130),
                    "면적_km2": meta["면적"],
                })
    return pd.DataFrame(rows)

df = load_data()

# ─────────────────────────────────────────────
# SRS 계산
# ─────────────────────────────────────────────
def calc_srs(sub_df: pd.DataFrame) -> tuple[float, str, str]:
    """창업 위험도 점수 (0–100) 및 등급 반환"""
    recent = sub_df[sub_df["연도"] >= 2023]
    total_open  = recent["개업수"].sum()
    total_close = recent["폐업수"].sum()
    closure_rate = total_close / max(total_open, 1)

    latest = sub_df[sub_df["연도"] == 2025].iloc[0]
    prev   = sub_df[sub_df["연도"] == 2024].iloc[0]
    density = latest["현재매장수"] / max(latest["면적_km2"], 1)
    density_norm = min(density / 10, 1.0)  # 0–1 정규화
    growth = (latest["개업수"] - prev["개업수"]) / max(prev["개업수"], 1)
    growth_penalty = max(-growth, 0)  # 감소할수록 위험

    raw = closure_rate * 40 + density_norm * 35 * 100 + growth_penalty * 25 * 100
    score = min(round(raw, 1), 100.0)
    score = max(score, 0.0)

    if score <= 35:
        return score, "창업 유망 🟢", "safe"
    elif score <= 60:
        return score, "진입 주의 🟡", "caution"
    else:
        return score, "고위험 상권 🔴", "danger"

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 12px 0 20px 0;'>
        <span style='font-size:24px; font-weight:800; color:#1A1A18; letter-spacing:-0.03em;'>🥐 BakeMap</span><br>
        <span style='font-size:12px; color:#9B9B8F; font-weight:500;'>베이커리 상권 분석 플랫폼</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📍 분석 지역 선택**")
    selected_district = st.selectbox("자치구", list(DISTRICTS.keys()), label_visibility="collapsed")
    dongs = DISTRICTS[selected_district]["동"]
    selected_dong = st.selectbox("행정동", dongs, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📅 분석 기간**")
    year_range = st.slider("연도 범위", 2019, 2025, (2021, 2025), label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🔍 비교 지역** (선택)")
    compare_districts = [d for d in DISTRICTS.keys() if d != selected_district]
    compare_district = st.selectbox("비교 자치구", ["없음"] + compare_districts, label_visibility="collapsed")
    compare_dong = None
    if compare_district != "없음":
        compare_dong = st.selectbox(
            "비교 행정동",
            DISTRICTS[compare_district]["동"],
            label_visibility="collapsed"
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#C0BFBA; line-height:1.7;'>
    데이터 출처: 서울 열린데이터 광장<br>
    서울시 제과점영업 인허가 정보<br>
    (데모용 모의 데이터 사용 중)
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 데이터 필터
# ─────────────────────────────────────────────
mask = (
    (df["자치구"] == selected_district) &
    (df["행정동"] == selected_dong) &
    (df["연도"].between(*year_range))
)
area_df   = df[mask].sort_values("연도")
latest_yr = area_df[area_df["연도"] == area_df["연도"].max()].iloc[0]
prev_yr   = area_df[area_df["연도"] == (area_df["연도"].max() - 1)].iloc[0]
srs_score, srs_label, srs_cls = calc_srs(area_df)

# ─────────────────────────────────────────────
# 메인 헤더
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="page-title">{selected_district} {selected_dong}</div>
<div class="page-subtitle">베이커리 상권 분석 리포트 · {year_range[0]}–{year_range[1]}</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI 카드 (5열)
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def kpi(col, label, value, delta=None, delta_label="전년 대비"):
    delta_html = ""
    if delta is not None:
        sign = "up" if delta >= 0 else "down"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f"<div class='kpi-delta {sign}'>{arrow} {abs(delta)} {delta_label}</div>"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

kpi(c1, "현재 매장 수",  f"{int(latest_yr['현재매장수'])}개")
kpi(c2, "최근 개업",     f"{int(latest_yr['개업수'])}건",  int(latest_yr['개업수'] - prev_yr['개업수']),  "건")
kpi(c3, "최근 폐업",     f"{int(latest_yr['폐업수'])}건",  int(latest_yr['폐업수'] - prev_yr['폐업수']),  "건")
survival = round(1 - area_df["폐업수"].sum() / max(area_df["개업수"].sum(), 1), 2)
kpi(c4, "누적 생존율",   f"{int(survival*100)}%")

# SRS 카드
badge_cls = {"safe": "srs-safe", "caution": "srs-caution", "danger": "srs-danger"}[srs_cls]
c5.markdown(f"""
<div class="kpi-card" style="height:110px;">
    <div class="kpi-label">창업 위험도 (SRS)</div>
    <div class="kpi-value">{srs_score:.0f}<span style="font-size:16px;font-weight:500;color:#9B9B8F;"> / 100</span></div>
    <div><span class="srs-badge {badge_cls}">{srs_label}</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 탭 레이아웃
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈  개·폐업 추이", "🗺  밀집도 분석", "🏆  유사 상권 비교"])

# ────────── TAB 1: 추이 ──────────
with tab1:
    left, right = st.columns([3, 1], gap="large")

    with left:
        st.markdown('<div class="section-header">연도별 개·폐업 현황</div>', unsafe_allow_html=True)

        # 비교 데이터
        compare_df = None
        if compare_district != "없음" and compare_dong:
            compare_df = df[
                (df["자치구"] == compare_district) &
                (df["행정동"] == compare_dong) &
                (df["연도"].between(*year_range))
            ].sort_values("연도")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=area_df["연도"], y=area_df["개업수"],
            name=f"개업 ({selected_dong})",
            marker_color=COLOR_OPEN, opacity=0.85,
            marker_cornerradius=4,
        ))
        fig.add_trace(go.Bar(
            x=area_df["연도"], y=-area_df["폐업수"],
            name=f"폐업 ({selected_dong})",
            marker_color=COLOR_CLOSE, opacity=0.85,
            marker_cornerradius=4,
        ))
        # 비교 지역 라인
        if compare_df is not None and not compare_df.empty:
            net = compare_df["개업수"] - compare_df["폐업수"]
            fig.add_trace(go.Scatter(
                x=compare_df["연도"], y=net,
                mode="lines+markers",
                name=f"순증가 ({compare_dong})",
                line=dict(color="#A78BFA", width=2, dash="dot"),
                marker=dict(size=6),
            ))

        fig.update_layout(
            **CHART_LAYOUT,
            barmode="overlay",
            yaxis_title="매장 수 (개업 +, 폐업 −)",
            xaxis=dict(tickmode="linear", dtick=1, showgrid=False),
            yaxis=dict(gridcolor="#F0EEE9", zeroline=True, zerolinecolor="#DDDBD5"),
            height=340,
        )
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 누적 순증감
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">누적 순증감 추이</div>', unsafe_allow_html=True)
        area_df2 = area_df.copy()
        area_df2["순증감"] = area_df2["개업수"] - area_df2["폐업수"]
        area_df2["누적"] = area_df2["순증감"].cumsum()

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=area_df2["연도"], y=area_df2["누적"],
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.12)",
            line=dict(color=COLOR_OPEN, width=2),
            mode="lines+markers",
            marker=dict(size=7, color=COLOR_OPEN),
            name="누적 순증감",
        ))
        fig2.update_layout(
            **CHART_LAYOUT,
            height=220,
            yaxis=dict(gridcolor="#F0EEE9", zeroline=True, zerolinecolor="#DDDBD5"),
            xaxis=dict(tickmode="linear", dtick=1, showgrid=False),
        )
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-header">데이터 인사이트</div>', unsafe_allow_html=True)

        total_open_n  = int(area_df["개업수"].sum())
        total_close_n = int(area_df["폐업수"].sum())
        net_n = total_open_n - total_close_n

        # 추세 판단
        recent_3 = area_df[area_df["연도"] >= area_df["연도"].max() - 2]
        close_gt_open = (recent_3["폐업수"] > recent_3["개업수"]).sum()

        if close_gt_open >= 2:
            ins_cls, ins_icon, ins_msg = "bad", "⚠️", (
                f"최근 3년 중 {close_gt_open}년 연속 폐업이 개업을 초과했습니다. "
                "상권 포화 또는 수요 위축 가능성이 높으니 진입 전 면밀한 검토가 필요합니다."
            )
        elif srs_score <= 35:
            ins_cls, ins_icon, ins_msg = "good", "✅", (
                "개업 증가율이 안정적이고 폐업률이 낮은 유망 상권입니다. "
                "데이터상 창업 리스크가 상대적으로 낮게 측정되었습니다."
            )
        else:
            ins_cls, ins_icon, ins_msg = "warn", "🔔", (
                "개업과 폐업이 비슷한 수준으로 유지되는 안정 국면입니다. "
                "경쟁 강도를 추가로 확인한 후 진입 여부를 결정하세요."
            )

        st.markdown(f'<div class="insight-box insight-{ins_cls}">{ins_icon} {ins_msg}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 요약 통계
        stats = {
            "기간 총 개업": f"{total_open_n}건",
            "기간 총 폐업": f"{total_close_n}건",
            "기간 순 증감": f"{'▲' if net_n >= 0 else '▼'} {abs(net_n)}건",
            "폐업률 (기간)": f"{round(total_close_n/max(total_open_n,1)*100)}%",
            "분석 행정동": f"{selected_district} {selected_dong}",
        }
        for k, v in stats.items():
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;padding:10px 0;
                        border-bottom:1px solid #ECECEA;font-size:13px;'>
                <span style='color:#9B9B8F;font-weight:500;'>{k}</span>
                <span style='color:#1A1A18;font-weight:700;'>{v}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SRS 게이지
        st.markdown('<div style="font-size:13px;font-weight:600;color:#1A1A18;margin-bottom:8px;">위험도 점수 상세</div>', unsafe_allow_html=True)
        gauge_color = {"safe": COLOR_SAFE, "caution": COLOR_WARN, "danger": COLOR_DANGER}[srs_cls]
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=srs_score,
            number={"suffix": "점", "font": {"size": 28, "color": "#1A1A18"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "transparent"},
                "bar": {"color": gauge_color, "thickness": 0.25},
                "bgcolor": "#F0EEE9",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35],  "color": "#EAF7F0"},
                    {"range": [35, 60], "color": "#FFF4E0"},
                    {"range": [60, 100],"color": "#FEECEB"},
                ],
                "threshold": {
                    "line": {"color": gauge_color, "width": 3},
                    "thickness": 0.85,
                    "value": srs_score,
                },
            },
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Pretendard, sans-serif",
            height=180, margin=dict(l=10, r=10, t=10, b=0),
        )
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(f'<div style="text-align:center;margin-top:-12px;"><span class="srs-badge srs-{srs_cls}">{srs_label}</span></div>', unsafe_allow_html=True)


# ────────── TAB 2: 밀집도 ──────────
with tab2:
    st.markdown('<div class="section-header">자치구별 현재 매장 밀집도</div>', unsafe_allow_html=True)

    latest_all = df[df["연도"] == 2025]
    density_df = (
        latest_all.groupby("자치구")
        .agg(총매장수=("현재매장수", "sum"), 면적=("면적_km2", "first"))
        .reset_index()
    )
    density_df["밀집도_km2"] = (density_df["총매장수"] / density_df["면적"]).round(2)
    density_df = density_df.sort_values("밀집도_km2", ascending=True)

    fig3 = go.Figure(go.Bar(
        x=density_df["밀집도_km2"],
        y=density_df["자치구"],
        orientation="h",
        marker_color=[
            COLOR_OPEN if d == selected_district else "#CBD5E1"
            for d in density_df["자치구"]
        ],
        marker_cornerradius=4,
        text=density_df["밀집도_km2"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        textfont=dict(size=12, color="#1A1A18"),
    ))
    fig3.update_layout(
        **CHART_LAYOUT,
        height=320,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False),
        margin=dict(l=0, r=40, t=36, b=0),
    )
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">행정동별 매장 수 분포 (선택 자치구)</div>', unsafe_allow_html=True)

    dong_latest = df[(df["자치구"] == selected_district) & (df["연도"] == 2025)]
    dong_agg = dong_latest.groupby("행정동")["현재매장수"].sum().reset_index().sort_values("현재매장수", ascending=False)

    fig4 = go.Figure(go.Bar(
        x=dong_agg["행정동"],
        y=dong_agg["현재매장수"],
        marker_color=[
            COLOR_OPEN if d == selected_dong else "#CBD5E1"
            for d in dong_agg["행정동"]
        ],
        marker_cornerradius=6,
        text=dong_agg["현재매장수"],
        textposition="outside",
        textfont=dict(size=12),
    ))
    fig4.update_layout(
        **CHART_LAYOUT,
        height=280,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, showticklabels=False),
    )
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ────────── TAB 3: 비교 ──────────
with tab3:
    key = f"{selected_district} {selected_dong}"
    recs = RECOMMENDATIONS.get(key, [
        ("마포구 성산동", 38, "+2.1%"),
        ("은평구 신사동", 41, "+1.8%"),
        ("성동구 성수동", 32, "+3.4%"),
    ])

    col_rec, col_chart = st.columns([1, 2], gap="large")

    with col_rec:
        st.markdown('<div class="section-header">추천 대안 상권</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:13px;color:#9B9B8F;margin-bottom:16px;line-height:1.6;">
        <b>{selected_dong}</b>과 유사한 조건의 상권 중<br>
        위험도가 낮고 성장 가능성이 높은 지역입니다.
        </div>
        """, unsafe_allow_html=True)

        for name, score, growth in recs:
            score_cls = "srs-safe" if score <= 35 else ("srs-caution" if score <= 60 else "srs-danger")
            st.markdown(f"""
            <div class="rec-card">
                <div>
                    <div class="rec-name">📍 {name}</div>
                    <div style="font-size:12px;color:#9B9B8F;margin-top:4px;">최근 개업 증가율 {growth}</div>
                </div>
                <div style="text-align:right;">
                    <span class="srs-badge {score_cls}">{score}점</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        st.markdown('<div class="section-header">현재 지역 vs 추천 지역 SRS 비교</div>', unsafe_allow_html=True)
        compare_names  = [f"{selected_dong} (현재)"] + [r[0].split(" ")[1] for r in recs]
        compare_scores = [srs_score] + [r[1] for r in recs]
        compare_colors = [
            COLOR_OPEN if i == 0 else (
                COLOR_SAFE if s <= 35 else (COLOR_WARN if s <= 60 else COLOR_DANGER)
            )
            for i, s in enumerate(compare_scores)
        ]

        fig5 = go.Figure(go.Bar(
            x=compare_names,
            y=compare_scores,
            marker_color=compare_colors,
            marker_cornerradius=8,
            text=[f"{s:.0f}점" for s in compare_scores],
            textposition="outside",
            textfont=dict(size=13, color="#1A1A18"),
        ))
        fig5.update_layout(
            **CHART_LAYOUT,
            height=320,
            yaxis=dict(range=[0, 110], showgrid=False, showticklabels=False),
            xaxis=dict(showgrid=False),
        )
        # 기준선
        fig5.add_hline(y=35, line_dash="dot", line_color=COLOR_SAFE,   annotation_text="유망 기준",   annotation_font_size=11)
        fig5.add_hline(y=60, line_dash="dot", line_color=COLOR_WARN,   annotation_text="주의 기준",   annotation_font_size=11)

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 하단 리포트 CTA
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<hr style="border:none;border-top:1px solid #ECECEA;margin:0 0 24px 0;">', unsafe_allow_html=True)

btn_col, text_col = st.columns([1, 3])
with btn_col:
    if st.button("📄 PDF 리포트 생성", use_container_width=True, type="primary"):
        st.info("🔒 비즈니스 플랜 구독 시 이용 가능합니다. 구독하면 선택 지역 전체 분석 리포트를 PDF로 즉시 다운로드할 수 있습니다.")
with text_col:
    st.markdown("""
    <div style="font-size:13px;color:#9B9B8F;padding-top:10px;line-height:1.7;">
    리포트에는 <b>상권 요약 · 시계열 차트 · SRS 점수 · 추천 지역</b>이 포함됩니다.<br>
    창업 계획서, 투자 제안서, 금융기관 대출 심사 서류에 활용 가능합니다.
    </div>
    """, unsafe_allow_html=True)
