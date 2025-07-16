from http.client import responses

import requests
from bs4 import BeautifulSoup
import lxml
from config import URL, HEADERS
from utils.excel_utils import find_articles
from time import sleep




def create_session():
    session = requests.Session()
    return session

def login(session, login_url, login_data, headers):
    response_enter = session.get(url=login_url, headers=headers)
    sleep(3)
    response_login = session.post(url=login_url, data=login_data, headers=headers)

    if response_login.status_code == 200 and "Безубик Н.Ю." in response_login.text:
        print("Авторизация http://moytok.ru/ прошла успешна")
        return True
    else:
        print("Не получилось подключиться к http://moytok.ru/")
        return False


def search_product_by_article(session, search_url):
    articles = find_articles()[:40]
    articles_price = dict()
    print(f"\n{'Артикул'.ljust(40)}{'Цена'}")  # Заголовки
    print("-" * 80)
    for article in articles:
        sleep(2)
        response = session.get(f'{search_url}{article}')
        print(response.status_code)
        if response.status_code == 200 and "Нет товаров, соответствующих критериям поиска." not in response.text:
            soup = BeautifulSoup(response.text, 'lxml')
            price = soup.find("div", class_="product-layout").find("p", class_="price").text.strip()
            articles_price[article] = price
            print(f'{article.ljust(40)}| {price}')
    print(articles_price)



def main():
    headers = HEADERS
    url = URL.get(1)["site"]
    login_url = f"{url}index.php?route=account/login"
    search_url = f"{url}index.php?route=product/search&search="
    login_data = URL.get(1)["data"]

    session = create_session()

    # Авторизация
    if login(session, login_url, login_data, headers):
        # Если авторизация успешна, парсим страницу
        soup = search_product_by_article(session, search_url)

        if soup:
            # Пример поиска данных на странице
            title = soup.find('h1').text
            print(f"Заголовок на странице: {title}")
        else:
            print("Не удалось распарсить страницу.")
    else:
        print("Не удалось авторизоваться.")


main()