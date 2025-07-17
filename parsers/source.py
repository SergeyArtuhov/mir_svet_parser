from config import URL, HEADERS
from moytok import create_session
from moytok import login
from moytok import search_product_by_article
from my_gui import window_gui

def main():

    app = window_gui()

    headers = HEADERS
    url = URL.get(1)["site"]
    login_url = f"{url}index.php?route=account/login"
    search_url = f"{url}index.php?route=product/search&search="
    login_data = URL.get(1)["data"]

    session = create_session()

    # Авторизация
    if login(session, login_url, login_data, headers, app):
        # Если авторизация успешна, парсим страницу
        soup = search_product_by_article(session, search_url, app, app.file_path)

        if soup:
            # Пример поиска данных на странице
            title = soup.find('h1').text
            print(f"Заголовок на странице: {title}")
        else:
            print("Не удалось распарсить страницу.")
    else:
        print("Не удалось авторизоваться.")


main()