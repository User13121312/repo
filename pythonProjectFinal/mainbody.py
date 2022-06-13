import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import time
from dateutil.parser import parse
from datetime import date, timedelta
import re
import requests
from PIL import Image

with st.echo(code_location='below'):
    """
    ## Заголовок проекта
    """
    st.write(f"### Hello, User!")

    """
    ## Сбор данных
    Я собираюсь посмотреть публикации в Одноклассниках, содержащие фразу "погиб на Украине". 
     Я использую selenium, чтобы залогиниться и открыть нужную страницу с поиском. 
    """

    def open_ok():
        global driver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = uc.Chrome()
        start_url = 'https://m.ok.ru/dk?st.cmd=globalContentSearch&st.search=%D1%81%D0%B5%D0%B3%D0%BE%D0%B4%D0%BD%D1%8F&st.frwd=on&st.page=1&_prevCmd=globalContentSearchSettings&tkn=767'
        driver.get(start_url)
        st.image(driver.get_screenshot_as_png())

        login = driver.find_element(By.ID, "field_login")
        login.send_keys('79151089738')
        password = driver.find_element(By.ID, "field_password")
        password.send_keys('Oklahoma1837748')
        st.image(driver.get_screenshot_as_png())

        enter_buttom = driver.find_element(By.CLASS_NAME, "base-button_target")
        enter_buttom.click()
        time.sleep(1)
        st.image(driver.get_screenshot_as_png())
        real_url = 'https://ok.ru/dk?st.cmd=searchResult&st.mode=Content&st.grmode=Groups&st.query=%D0%BF%D0%BE%D0%B3%D0%B8%D0%B1%20%D0%BD%D0%B0%20%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B5'
        driver.get(real_url)

    def scroll():
        global driver
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.8)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                try:
                    driver.find_element(By.ID, 'load-more').click()
                except:
                    break
            last_height = new_height

    #open_ok()

    #вспомогательная функция, скачивающая данные с j постов, начиная с поста под номером i
    def parse_urls(i=0, j=100):
        global urls
        dates = []
        groups = []
        texts = []
        yesterday = (date.today() - timedelta(days=1)).strftime('%m.%d.%y')
        date_dict = {'вчера': yesterday, 'янв': 'january', 'фев': 'february', 'марта': 'march', 'апр': 'april',
                     'мая': 'may', 'июн': 'june', 'июл': 'july', 'авг': 'august', 'сен': 'september', 'окт': 'october',
                     'ноя': 'november', 'дек': 'december'}
        for url in urls[i:i + j]:
            time.sleep(3)
            r = requests.get(url)
            soup = BeautifulSoup(r.text)
            try:
                rough_date = soup.find(class_='ucard_add-info_i').text
                match = re.search(r'[^0-9 ]+', rough_date).group(0)
                dates.append(parse(rough_date.replace(match, date_dict[match])))
            except:
                try:
                    dates.append(parse(rough_date))
                except:
                    dates.append(None)
            try:
                post_text = soup.find(class_='media-text_cnt_tx emoji-tx textWrap').text
                texts.append(post_text)
            except:
                texts.append(None)
            try:
                groups.append(soup.find(class_="group-link").text)
            except:
                groups.append(None)
        return dates, groups, texts

    #эта функция может быть запущена, но я буду использовать таблицу  уже скачанными данными
    def download_data():
        global urls, all_dates, all_groups, all_texts
        urls = []
        posts = driver.find_elements(By.CLASS_NAME, "media-text_a")
        urls = [media.get_attribute('href') for media in posts]
        all_dates = []
        all_groups = []
        all_texts = []
        for i in [0, 100, 200, 300, 400, 500, 600, 700, 800]:
            parsed_i_j = parse_urls(i)
            all_dates = all_dates + parsed_i_j[0]
            all_groups = all_groups + parsed_i_j[1]
            all_texts = all_texts + parsed_i_j[2]
            time.sleep(10)
        parsed_i_j = parse_urls(900, 71)
        all_dates = all_dates + parsed_i_j[0]
        all_groups = all_groups + parsed_i_j[1]
        all_texts = all_texts + parsed_i_j[2]
        return pd.DataFrame({'url': urls, 'date': all_dates, 'group': all_groups, 'text': all_texts})

    @st.cache
    def get_data():
       return pd.read_csv(r'C:\Users\1\Downloads\OK_data.csv')[['url', 'date', 'group', 'text']]

    df = get_data()
    """
    При скачивании данных beautifulsoup медленно просматривал каждый пост, чтобы не нарваться на блокировку. 
    Я использую регулярные выражения, свой словарь и дополнительные библиотеки, чтобы записать время публикации в удобном формате.
    
        yesterday = (date.today() - timedelta(days=1)).strftime('%m.%d.%y')
        date_dict = {'вчера': yesterday, 'янв': 'january', 'фев': 'february', 'марта': 'march', 'апр': 'april',
                     'мая': 'may', 'июн': 'june', 'июл': 'july', 'авг': 'august', 'сен': 'september', 'окт': 'october',
                     'ноя': 'november', 'дек': 'december'}
    Словарь позволяет преобразовывать строчки вида:
        
        11 марта
    Пришлось не раз использовать окружение try, потому что не всегда получалось найти нужный класс на странице.
    #### Давайте оцень, что получилось. 
    Я заметил, что Одноклассники сообщали, что по моему запросу найдено 22 тысячи постов, но отображается только 971. Что это за посты?
    """

    def time_plot():
        global df
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        time_check = df['date'].apply(lambda x: pd.to_datetime(x) > parse('24 february 2022'))
        ax1.histplot(df[time_check]['date'], bins=15)
        ax1.tick_params(axis="x", labelrotation=90)
        ax1.set_title("Распределение по времени публикации после 24.02")
        ax2.hist(df['date'], bins=15)
        ax2.tick_params(axis="x", labelrotation=90)
        ax2.set_title("Распределение по времени публикации за всё время")
        st.pyplot(fig)

    # картинка получена почти что этим же кодом, но в юпитере
    image = Image.open('figonline.png')
    st.image(image, caption='Соцсеть склонна показывает самые последние посты')

    no_na_df = df.dropna()
    st.write(f'##### Размер изначального датафрейма: {len(df)}')
    st.write(f'##### Размер датафрейма без None-ов: {len(no_na_df)}')

    """ 
    Потери есть, но они не критичные. Тем более, что их можно частично залатать! Сначала добавим к датафрейму ещё две колонки:
    предполагаемое имя убитого, для него я использую регулярное выражение, и место для заметок.
    """
    def modify_df():
        global df
        name = []
        for i in range(971):
            text = df.loc[i]['text']
            try:
                name.append(re.search(
                    r'(?!На|В|Респуб|Белый|МИД|Укр|Мино|Гвард|Чех|День|Рос|Могой)[А-ЯЁ]+[а-яё]+ [А-ЯЁ]+[а-яё]+( [А-ЯЁ]+[а-яё]+|)',
                    text).group(0))
            except:
                name.append(None)
        df['name'] = name
        df['user notes'] = [{'added': False} for x in range(len(df))]
    modify_df()
    df[200:210]

    """
    #### Поучавствуйте в заполнении пропущенной информации!
    Давайте поищем неотредактированные строчки с именем Александр
    """
    the_name = st.text_input(label='', value = 'Александр', help = ':))))))))))))))))))))')
    added_check_series = df['user notes'].apply(lambda x: not x['added'] )
    name_check_series = df['name'].apply(lambda x: x != None and the_name in x and 'ович' not in x )
    the_chosen = df.index[name_check_series & added_check_series][0]
    st.table(df.loc[the_chosen][['url', 'date', 'group', 'text', 'name']])

    actual_name = st.text_input(label='ФИО из текста', value = None)
    actual_toponim = st.text_input(label='Топоним из текста', value = None)
    df.loc[the_chosen]['user notes']['added'] = True
    df.loc[the_chosen]['user notes']['actual_name'] = actual_name
    df.loc[the_chosen]['user notes']['actual_toponim'] = actual_toponim
    df.loc[the_chosen]['user notes']


