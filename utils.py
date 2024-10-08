import time

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import folium_static


def search_latlon(address: str) -> list[float, float]:
    """
    住所から緯度経度を取得する
    """
    time.sleep(1)
    base_address = "京都市"
    address = base_address + address
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    params = {"q": address}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        response_data = r.json()
        if response_data and 'geometry' in response_data[0]:
            coords = r.json()[0]["geometry"]["coordinates"]
            return coords[0], coords[1]
        else:
            print(f'緯度経度が見つかりません: {address}')
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")
        return None, None


def show_data(df: pd.Series, num: int):

    info = {
        "事業所名": df["事業所名"],
        "法人名": df["法人名称"],
        "事業所所在地": df["事業所所在地"],
        "電話番号": df["電話番号"],
        "FAX番号": df["FAX番号"],
        "事業所番号": df["事業所番号"]
    }

    st.write(f"施設詳細 {num+1}")
    c = st.container(border=True)

    for key, value in info.items():
        c.write(f"{key}: {value}")


def add_latlon(df: pd.DataFrame) -> pd.DataFrame:
    '''
    事業所所在地から緯度経度を取得し、データフレームを追加する
    '''
    missing_latlon = df[df['lat'].isna() | df['lon'].isna()]

    if not missing_latlon.empty:
        missing_latlon[['lat', 'lon']] = missing_latlon['事業所所在地'].apply(lambda x: pd.Series(search_latlon(x)))
        df.update(missing_latlon)
    return df


def draw_map(df: pd.DataFrame):
    df1 = df.dropna()
    if df.empty | df1.empty:
        return st.write('位置情報が見つかりませんでした。')
    center = df1.iloc[0, -1], df.iloc[0, -2]
    print(center)
    m = folium.Map(location=center, zoom_start=12, height=300, width=700)
    for i in range(len(df1)):
        position = df1.iloc[i, -1], df1.iloc[i, -2]
        name = df1.iloc[i, 3]
        folium.Marker(
            position, popup=name, tooltip=name
        ).add_to(m)
    st_map = folium_static(m, height=300)

