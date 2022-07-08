from __future__ import print_function
import gspread
from google.oauth2 import service_account
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie
import streamlit as st
import streamlit.components.v1 as components


@st.cache
def get_data():
    SCOPE = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    SERVICE_FILE = "Pbpython-key.json"
    SPREADSHEET = "Balance of Life"

    credentials = service_account.Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPE)

    gc = gspread.authorize(credentials)
    workbook = gc.open(SPREADSHEET)
    sheet = workbook.sheet1
    df = pd.DataFrame(sheet.get_all_records())
    return df


@st.cache
def draw_rosechart(names, values):
    the_title = 'Balance of Life for ' + values[-1]
    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(names, values)],
            radius=["10%", "75%"],
            center=["30%", "50%"],
            rosetype="area",
            label_opts=opts.LabelOpts(is_show=True, formatter="{b}: {c}"),
    )
        .add(
            "",
            [['10', 10]],
            radius=["74.6%", "75%"],
            center=["30%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=the_title, pos_left="0%"),
                         legend_opts=opts.LegendOpts(is_show=False))
        .render("pie_rosetype.html")
    )


df = get_data()
users = df['Ваше имя']
option = st.selectbox(
     'Инфографика какого человека вам интересна?',
     users)
st.write('Вы выбрали:', option)
#st.write(df.loc[df['Ваше имя'] == option])

names = list(df.loc[df['Ваше имя'] == option].columns)[1:]
values = list(df.loc[df['Ваше имя'] == option].values[0])[1:]
#st.write(names, values)
draw_rosechart(names, values)
with open('pie_rosetype.html', 'r') as f:
    html_string = f.read()
components.html(html_string, height=500)



