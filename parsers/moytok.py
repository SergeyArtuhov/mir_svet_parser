from http.client import responses

import tkinter as tk
import requests
from bs4 import BeautifulSoup
import lxml
from config import URL, HEADERS
from excel_utils import find_articles
#from utils.excel_utils import find_articles
from time import sleep
import random

def rand_sleep() :
    delay = random.uniform(1.5, 3.5)
    sleep(delay) 

def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session

def login(session, login_url, login_data, headers, app):
    app.update_output("Попытка авторизации...\n")
    return True
    #response_enter = session.get(url=login_url, headers=headers)
    #sleep(3)
    #response_login = session.post(url=login_url, data=login_data, headers=headers)
#
    #if response_login.status_code == 200 and "Безубик Н.Ю." in response_login.text:
    #    print("Авторизация http://moytok.ru/ прошла успешна")
    #    return True
    #else:
    #    print("Не получилось подключиться к http://moytok.ru/")
    #    return False


def search_product_by_article(session, search_url, app, file_path):
    articles = find_articles(file_path)[:40]
    articles_price = dict()
    total_articles = len(articles)
    app.parsed_data = []
    app.update_output(f"\n{'Артикул'.ljust(40)}{'Цена'}\n")
    app.update_output("-" * 80 + "\n")
    #print(f"\n{'Артикул'.ljust(40)}{'Цена'}")  # Заголовки
    #print("-" * 80)
    for article in articles:
        if app.stop_parsing:
            app.update_output("Парсинг был отменён.\n")
            break

        rand_sleep()
        response = session.get(f'{search_url}{article}')
        app.root.after(0, lambda: app.update_progress(i, total_articles))
        #print(response.status_code)
        if response.status_code == 200 and "Нет товаров, соответствующих критериям поиска." not in response.text:
            soup = BeautifulSoup(response.text, 'lxml')
            price = soup.find("div", class_="product-layout").find("p", class_="price").text.strip()
            articles_price[article] = price
            app.update_output(f'{article.ljust(40)}| {price}\n')
            app.parsed_data.append([article, price])
            #print(f'{article.ljust(40)}| {price}')
    #app.update_output(f"Результаты: {articles_price}\n")
    app.root.after(0, lambda: app.export_btn.config(state=tk.NORMAL))
    #print(articles_price)