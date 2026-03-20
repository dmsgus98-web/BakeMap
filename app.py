import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="BakeMap",
    page_icon="🥐",
    layout="wide"
)

# -----------------------------
# 스타일 (세련된 UI)
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f8f9fb;
}
.card {
    padding: 20px;
    border-radius: 16px;
    background-color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}
.metric {
    font-size: 24px;
    font-weight: 700;
}
.sub {
    color: gray;
    font-size: 14px;
}
.title {
    font-size: 32px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 더미 데이터 (MVP용)
# -----------------------------
@st.cache_data
def load_data():
    data = pd.DataFrame({
        "행정동": ["연남동", "성산동", "신사동", "성수동", "잠실동"],
        "매장수": [20, 12, 15, 18, 25],
        "신규개업": [4, 6, 5, 8, 3],
        "폐업": [6, 2, 3, 4, 7],
        "위험도": [71, 38, 41, 32, 75]
    })
    return data

df = load_data()

# -----------------------------
# 헤더
# -----------------------------
st.markdown('<div class="title">🥐 BakeMap</div>', unsafe_allow_html=True)
st.markdown("데이터 기반 베이커리 창업 입지 분석 서비스")

st.divider()

# -----------------------------
# 검색 영역
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    selected = st.selectbox(
        "📍 분석할 지역을 선택하세요",
        df["행정동"]
    )

with col2:
    st.markdown("")
    st.markdown("")
    if st.button("🔍 분석하기", use_container_width=True):
        st.session_state["run"] = True

# -----------------------------
# 결과 표시
# -----------------------------
if st.session_state.get("run"):

    data = df[df["행정동"] == selected].iloc[0]

    st.divider()

    st.subheader(f"📊 {selected} 상권 분석")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="sub">현재 매장 수</div>
            <div class="metric">{data['매장수']}개</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="sub">최근 1년 개업</div>
            <div class="metric">{data['신규개업']}건</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="sub">최근 1년 폐업</div>
            <div class="metric">{data['폐업']}건</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        color = "green" if data["위험도"] < 40 else "orange" if data["위험도"] < 70 else "red"

        st.markdown(f"""
        <div class="card">
            <div class="sub">창업 위험도</div>
            <div class="metric" style="color:{color}">{data['위험도']}점</div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------
    # 인사이트
    # -----------------------------
    st.divider()
    st.subheader("🧠 인사이트")

    if data["위험도"] >= 70:
        st.error("⚠️ 고위험 상권입니다. 폐업률 및 밀집도가 높습니다.")
    elif data["위험도"] >= 50:
        st.warning("⚠️ 진입 주의가 필요합니다.")
    else:
        st.success("✅ 비교적 안정적인 상권입니다.")

    # -----------------------------
    # 추천 지역
    # -----------------------------
    st.divider()
    st.subheader("💡 추천 지역")

    추천 = df.sort_values("위험도").head(3)

    for i, row in 추천.iterrows():
        st.markdown(f"""
        <div class="card">
            <b>{row['행정동']}</b> — 위험도 {row['위험도']}점
        </div>
        """, unsafe_allow_html=True)
