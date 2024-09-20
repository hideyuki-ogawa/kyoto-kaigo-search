import pandas as pd
import streamlit as st

from utils import show_data, draw_map, add_latlon

st.set_page_config(layout="wide")
df = pd.read_csv("./data/kaigo-all-20240901.csv")

st.write(
    """
# 京都市の介護施設探せます！

京都市の介護サービス等事業所一覧（令和6年9月1日現在）のデータを使用しています。

"""
)

areas = df["行政区"].unique()
services = df["サービス種類"].unique()

select_area = st.selectbox("介護施設を京都市の区を選択してください。", areas)
select_service = st.selectbox("探したいサービスを選択してください", services)


select_df = df[(df["行政区"] == select_area) & (df["サービス種類"] == select_service)]
show_df = select_df.loc[:, ["サービス種類", "事業所名", "事業所所在地"]]

st.write('''### 上のドロップダウンで選択された
         ''')
st.write('### 地域、サービスの施設が表示されます')
dataframe = st.dataframe(show_df, on_select="rerun")

df2 = select_df.iloc[dataframe.selection.rows, :]
if 'lat' not in df2.columns or 'lon' not in df2.columns:
    df2[['lat', 'lon']] = None, None 
# df2
if df not in st.session_state:
    st.session_state.df = df2

df2 = add_latlon(st.session_state.df)

st.write(f"## 選択施設数: {len(df2)}")

draw_map(df2)

for i in range(len(df2)):
    s1 = df2.iloc[i, :]
    show_data(s1, i)
