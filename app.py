import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

# 페이지 설정
st.set_page_config(page_title="BakeMap Admin - 분석가용", layout="wide")

# 1. Mock Data 생성 (기획안의 위경도 좌표 및 영업 상태 반영) [cite: 32]
@st.cache_data
def get_geo_data():
    # 서울 주요 베이커리 밀집 지역 샘플 좌표
    locations = {
        '연남동': [37.561, 126.924],
        '성수동': [37.544, 127.056],
        '한남동': [37.535, 127.001],
        '방배동': [37.483, 126.991]
    }
    data = []
    for name, coords in locations.items():
        for i in range(10):  # 지역당 10개의 가상 매장
            status = np.random.choice(['영업', '폐업'], p=[0.7, 0.3]) # 
            data.append({
                '상호명': f'{name} 베이커리 {i+1}호점',
                'lat': coords[0] + np.random.uniform(-0.005, 0.005),
                'lon': coords[1] + np.random.uniform(-0.005, 0.005),
                '영업상태': status,
                'SRS': np.random.randint(10, 90) # [cite: 67]
            })
    return pd.DataFrame(data)

df = get_geo_data()

st.title("🥐 BakeMap Interactive Map")
st.markdown("지도 위 마커에 마우스를 올리거나 클릭하여 상세 정보를 확인하세요.")

# 2. Folium 지도 생성
# 서울 중심부 좌표
m = folium.Map(location=[37.55, 126.98], zoom_start=12, tiles="cartodbpositron")

# 3. 데이터 포인트 추가 (Hover & Popup 기능) [cite: 56, 57]
for _, row in df.iterrows():
    # 영업 상태에 따른 마커 색상 구분 [cite: 57, 68]
    color = 'blue' if row['영업상태'] == '영업' else 'red'
    
    # Tooltip (커서를 대면 뜨는 정보)
    tooltip_text = f"<b>{row['상호명']}</b><br>위험도 점수: {row['SRS']}점"
    
    # Popup (클릭하면 뜨는 정보)
    popup_html = f"""
        <div style='width:150px'>
            <h4>{row['상호명']}</h4>
            <p>상태: <b>{row['영업상태']}</b></p>
            <p>SRS: {row['SRS']}점</p>
        </div>
    """
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        tooltip=tooltip_text,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# 4. Streamlit에 지도 렌더링
st_data = st_folium(m, width=1200, height=600)

# 5. 지도 인터랙션 결과 출력 (분석가용 사이드바)
if st_data['last_object_clicked_tooltip']:
    st.sidebar.success(f"선택된 매장 정보: {st_data['last_object_clicked_tooltip']}")
