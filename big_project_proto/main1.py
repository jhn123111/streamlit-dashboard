import pandas as pd
import numpy as np
import datetime
import joblib
from urllib.parse import quote
import branca
from geopy.geocoders import Nominatim
import ssl
from streamlit_option_menu import option_menu
import plotly.express as px

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from branca.colormap import linear
import branca.colormap as cmp
import geopandas

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------------------데이터 불러오기-------------------------------------------------------------
chart_data = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_sales.csv')
medal = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_medal.csv')

geo_json_data = requests.get(
    'https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json'
).json()

 # GeoJSON 데이터 중에서 구에 해당하는 부분만 추출
gangnam_geo_json = {
    "type": "FeatureCollection",
    "features": [feature for feature in geo_json_data["features"] if feature["properties"]["name"] == "강남구"]
}
songpa_gu_json = {
    "type": "FeatureCollection",
    "features": [feature for feature in geo_json_data["features"] if feature["properties"]["name"] == "송파구"]
}
seocho_gu_json = {
    "type": "FeatureCollection",
    "features": [feature for feature in geo_json_data["features"] if feature["properties"]["name"] == "서초구"]
    }
# -------------------------------------------------------------지도 불러오기 함수-------------------------------------------------------------
def show_map(lat, lon, zoom, data):

    df = pd.read_csv(BASE_DIR / "data" / "seoul_population.csv")


    #cctv 데이터 가져오기 !!경로 확인 필수!!
    gdf = geopandas.read_file(BASE_DIR / "data" / "cctv.geojson")


    #지도 포화도에 따른 색 표현
    linear = cmp.LinearColormap(
    [ 'green', 'yellow', 'red'],
    vmin = df.total.min(),
    vmax = df.total.max(),
    caption="population"

    )

    df_dict = df.set_index("district")["total"]

    m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles='CartoDB positron', attr='Map tiles by CortoDB positron, under CC BY 3.0. Data by OpenStreetMap, under ODbL.')


    folium.GeoJson(data,
                   name="population",
                   style_function=lambda feature: {
                       "fillColor": linear(df_dict[feature["properties"]["name"]]),
                        "color": "black",
                        "weight": 2,
                        "dashArray": "5, 5",
                       #지도위 색레이어 투명도
                        "fillOpacity":0.5,
                   },

                   highlight_function=lambda feature: {
                        "fillColor": (
                        "#ffc800"
                    ),
        },


                   zoom_on_click=True).add_to(m)

    #cctv 위치 마커 맵에 표시
    folium.GeoJson(
        gdf,
        name = "cctv",

        # 마커의 아이콘을 icon= 에서 바꿀 수 있음 fontawesome에서 가져오기 때문에 prefix='fa'를 꼭 붙여야함
        # https://fontawesome.com/v4/icons/

        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),


    ).add_to(m)

    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=2500, height=650)


    # cctv 데이터 스타일 - 너비 꽉 채우기
    st.markdown("""
            <style>
                table{
                    width:100%;
                }
            </style>

            """, unsafe_allow_html=True)

    #데이터 인덱스 1부터 시작
    gdf.index = np.arange(1, len(gdf)+1)

    #cctv 데이터 표시
    st.write(gdf)

# -------------------------------------------------------------홈페이지 탭 아이콘, 홈페이지 명 설정-------------------------------------------------------------
st.set_page_config(
        page_title= '빅프로젝트_10조',
        page_icon=":smile:",
        layout = "wide",
        initial_sidebar_state="expanded")

# -------------------------------------------------------------관제, 경로안내, 데이터 탭 내용 설정-------------------------------------------------------------

# -------------------------------------------------------------전체 설정-------------------------------------------------------------
def page4():
   # -------------------------------------------------------------사이드바 설정-------------------------------------------------------------


    st.markdown('<div style="text-align: center;"><h1>종합</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"}, # 아이콘 크기
            "nav-link": {"font-size" : "30px", # 글자 크기
                        "text-align" : "center", # 정렬
                        "margin" : "1px",  # 칸 사이 여백
                        "--hover-color": "#eee" #마우스 갖다댈 때 색,
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)

# -------------------------------------------------------------전체 관제 설정-------------------------------------------------------------
    if selected == "관제":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)

        show_map(37.56,127.25,11,geo_json_data)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader('위반 유형별')
            fig = px.pie(medal, names = "nation", values = "gold", hole=.3 )
            fig.update_traces(textposition='inside', textinfo = 'percent+label+value')
            fig.update_layout(font = dict(size = 14))
            fig.update(layout_showlegend=False)  # 범례 표시 제거
            st.plotly_chart(fig)

        with col2:
            st.subheader('1월 누적 견인 수')
            col2.metric("", "7회", "-2회")

        with col3:
            st.subheader('날짜별')
            col3.metric("", "115일", "20일")
# -------------------------------------------------------------전체 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.write("""
        The concept for this app was to compare Canadian terroir to that of the famous wine regions of the world.
        \nThere have been attempts at an app like this as a [research project](https://www.cgit.vt.edu/research/archive/vineyard-site-evaluation.html) but none in Canada and none at this scale.
        \nThis app was written in python using some HTML and CSS injections for customizing the frontend.
        """)
        st.write('')
        st.subheader('The Workflow')
        st.write("""
        1.\tCreate the profiles of the major wine regions using Google Earth Engine.
        \n2.\tCreate the profile for the queried location.
        \n3.\tCompare the queried location profile to all famous location profiles to find the most similar one.
        \n4.\tPass the results back to frontend for display.\n\n
        """)
        st.write('')
        st.write('')

        st.write("Here is the template I used when creating new location profiles following GeoJSON format:")

# -------------------------------------------------------------전체 데이터 설정-------------------------------------------------------------
    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)

def page1():
    # -------------------------------------------------------------사이드바 설정-------------------------------------------------------------


    st.markdown('<div style="text-align: center;"><h1>강남구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"}, # 아이콘 크기
            "nav-link": {"font-size" : "30px", # 글자 크기
                        "text-align" : "center", # 정렬
                        "margin" : "1px",  # 칸 사이 여백
                        "--hover-color": "#eee" #마우스 갖다댈 때 색,
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)

# -------------------------------------------------------------강남구 관제 설정-------------------------------------------------------------
    if selected == "관제":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)

        show_map(37.496,127.13,13,gangnam_geo_json)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader('위반 유형별')
            fig = px.pie(medal, names = "nation", values = "gold", hole=.3 )
            fig.update_traces(textposition='inside', textinfo = 'percent+label+value')
            fig.update_layout(font = dict(size = 14))
            fig.update(layout_showlegend=False)  # 범례 표시 제거
            st.plotly_chart(fig)

        with col2:
            st.subheader('1월 누적 견인 수')
            col2.metric("", "7회", "-2회")

        with col3:
            st.subheader('날짜별')
            col3.metric("", "115일", "20일")
# -------------------------------------------------------------강남구 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.write("""
        The concept for this app was to compare Canadian terroir to that of the famous wine regions of the world.
        \nThere have been attempts at an app like this as a [research project](https://www.cgit.vt.edu/research/archive/vineyard-site-evaluation.html) but none in Canada and none at this scale.
        \nThis app was written in python using some HTML and CSS injections for customizing the frontend.
        """)
        st.write('')
        st.subheader('The Workflow')
        st.write("""
        1.\tCreate the profiles of the major wine regions using Google Earth Engine.
        \n2.\tCreate the profile for the queried location.
        \n3.\tCompare the queried location profile to all famous location profiles to find the most similar one.
        \n4.\tPass the results back to frontend for display.\n\n
        """)
        st.write('')
        st.write('')

        st.write("Here is the template I used when creating new location profiles following GeoJSON format:")

# -------------------------------------------------------------강남구 데이터 설정-------------------------------------------------------------
    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
# -------------------------------------------------------------송파구 설정-------------------------------------------------------------
def page2():
    st.markdown('<div style="text-align: center;"><h1>송파구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"},
            "nav-link": {"font-size" : "30px",
                        "text-align" : "center",
                        "margin" : "0px",
                        "--hover-color": "#fffff",
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)
# -------------------------------------------------------------송파구 관제 설정-------------------------------------------------------------
    if selected == "관제":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        show_map(37.50,127.17,13,songpa_gu_json)
    #     data = pd.DataFrame({
    #     'lat':[37.51],
    #     'lon':[127.10]
    # })
    #     # 지도 그리기
    #     st.map(data,
    #           latitude='lat',
    #           longitude='lon')

# -------------------------------------------------------------송파구 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.write("""
        The concept for this app was to compare Canadian terroir to that of the famous wine regions of the world.
        \nThere have been attempts at an app like this as a [research project](https://www.cgit.vt.edu/research/archive/vineyard-site-evaluation.html) but none in Canada and none at this scale.
        \nThis app was written in python using some HTML and CSS injections for customizing the frontend.
        """)
        st.write('')
        st.subheader('The Workflow')
        st.write("""
        1.\tCreate the profiles of the major wine regions using Google Earth Engine.
        \n2.\tCreate the profile for the queried location.
        \n3.\tCompare the queried location profile to all famous location profiles to find the most similar one.
        \n4.\tPass the results back to frontend for display.\n\n
        """)
        st.write('')
        st.write('')

        st.write("Here is the template I used when creating new location profiles following GeoJSON format:")

# -------------------------------------------------------------송파구 데이터 설정-------------------------------------------------------------

    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
# -------------------------------------------------------------서초구 설정-------------------------------------------------------------
def page3():
    st.markdown('<div style="text-align: center;"><h1>서초구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"},
            "nav-link": {"font-size" : "30px",
                        "text-align" : "center",
                        "margin" : "0px",
                        "--hover-color": "#fffff",
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)
# -------------------------------------------------------------서초구 관제 설정-------------------------------------------------------------
    if selected == "관제":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        data = pd.DataFrame({
        'lat':[37.516, 37.51],
        'lon':[127.05, 127.10]
    })
        # 지도 그리기
        st.map(data,
              latitude='lat',
              longitude='lon')
# -------------------------------------------------------------서초구 견인관리 설정-------------------------------------------------------------
    if selected == "견인관리":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.write("""
        The concept for this app was to compare Canadian terroir to that of the famous wine regions of the world.
        \nThere have been attempts at an app like this as a [research project](https://www.cgit.vt.edu/research/archive/vineyard-site-evaluation.html) but none in Canada and none at this scale.
        \nThis app was written in python using some HTML and CSS injections for customizing the frontend.
        """)
        st.write('')
        st.subheader('The Workflow')
        st.write("""
        1.\tCreate the profiles of the major wine regions using Google Earth Engine.
        \n2.\tCreate the profile for the queried location.
        \n3.\tCompare the queried location profile to all famous location profiles to find the most similar one.
        \n4.\tPass the results back to frontend for display.\n\n
        """)
        st.write('')
        st.write('')

        st.write("Here is the template I used when creating new location profiles following GeoJSON format:")

# -------------------------------------------------------------서초구 데이터 설정-------------------------------------------------------------
    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)

# -------------------------------------------------------------사이드바 설정(사진)-------------------------------------------------------------
with st.sidebar:
    seoul_logo = {"image_url": BASE_DIR / "data" / "seoul_img.png"}

    #서울특별시
    #SEOUL MY SOUL https://www.seoul.go.kr/res_newseoul/images/seoul/seoulmysoul.png
    #휘장 https://www.seoul.go.kr/res_newseoul/images/seoul/img_seoullogo.png
    #해치 심벌 https://www.seoul.go.kr/res_newseoul/images/seoul/img_symbol1.png

    st.image(seoul_logo["image_url"])
# -------------------------------------------------------------사이드바 설정(강남구/송파구/서초구 선택)-------------------------------------------------------------
# 딕셔너리 선언 {  ‘selectbox항목’ : 페이지명 …  }
page_names_to_funcs = {'전체': page4, '강남구' : page1, '송파구': page2, '서초구': page3}

# 사이드 바에서 selectbox 선언 & 선택 결과 저장
selected_page = st.sidebar.selectbox('구를 선택하세요', page_names_to_funcs.keys())

# 해당 페이지 부르기
page_names_to_funcs[selected_page]()

st.markdown("""
         <style>
            h3, h2{
                text-align:center;
            }
         </style>


            """, unsafe_allow_html=True)


if selected_page == '강남구':
    with st.sidebar:
        # 사이 공간 조정
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")
        st.subheader('담당자')
        st.header('정지혜 주무관')
        st.subheader('연락처 010-0000-0000')

if selected_page == '송파구':
    with st.sidebar:
        st.subheader('담당자')
        st.header('남종하 주무관')
        st.subheader('연락처 010-0000-0000')
        st.markdown('<style>div[data-testid="stSidebar"] div div div{text-align: center;}</style>', unsafe_allow_html=True)
if selected_page == '서초구':
    with st.sidebar:
        st.subheader('담당자')
        st.header('배소영 주무관')
        st.subheader('연락처 010-0000-0000')
        st.markdown('<style>div[data-testid="stSidebar"] div div div{text-align: center;}</style>', unsafe_allow_html=True)


# streamlit run Desktop\BP\dashboard.py
