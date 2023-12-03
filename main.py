from http import HTTPStatus
from random import choice

import requests
from bs4 import BeautifulSoup

from utils import (save_items_to_csv, make_folder,
                   FailedRequestApi, logger)


def get_session():
    session = requests.Session()
    session.headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; "
        "x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/101.0.0.0 Safari/537.36"
    }
    return session


def get_proxy(session):
    html = session.get("https://free-proxy-list.net/").text
    soup = BeautifulSoup(html, "lxml")

    trs = soup.find("tbody").find_all("tr")

    proxies = []

    for tr in trs:
        tds = tr.find_all("td")
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        schema = "https" if "yes" in tds[6].text.strip() else "http"
        proxy = {"schema": schema, "address": ip + ":" + port}
        proxies.append(proxy)

    return choice(proxies)


def get_list_categories(session, proxy):
    url = "https://www.landingfolio.com/templates/"
    response = session.get(url, proxies=proxy)

    if response.status_code != HTTPStatus.OK:
        logger.error(f"Ответ сервера: {response.status_code}")
        raise FailedRequestApi(f"Ответ сервера: {response.status_code}")

    soup = BeautifulSoup(response.text, "lxml")
    categories = (
        soup.find("div", class_="space-y-2")
        .find_next_sibling("div", class_="space-y-2")
        .find_all("li", class_="flex")
    )

    result = [item.find("span").text for item in categories]
    return result


def get_data_all_categories(session, proxy, categories):
    base_url = "https://s3.landingfolio.com/template"

    for category in categories:
        category_url = f"{base_url}?category={category.lower()}"

        if category_url.__contains__(" "):
            category_url = category_url.replace(" ", "-")

        response = session.get(category_url, proxies=proxy)
        items = response.json()

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Ответ сервера: {response.status_code}")
            raise FailedRequestApi(f"Ответ сервера: {response.status_code}")

        # Если данные не пришли, пропускаем.
        if not items:
            continue

        folder_name = make_folder(category)
        for item in items:
            title = item.get("title")
            url = item.get("buyUrl")
            price = item["price"] if item["price"] else "Free"

            if not all([title, url, price]):
                logger.error("Структура JSON изменилась")
                raise KeyError("Структура JSON изменилась")

            data = {"title": title, "buyUrl": url, "price": price}

            save_items_to_csv(data, folder_name, category)

    return "Готово"


def main():
    session = get_session()
    proxy = get_proxy(session)
    categories = get_list_categories(session, proxy)
    return get_data_all_categories(session, proxy, categories)


if __name__ == "__main__":
    print(main())
