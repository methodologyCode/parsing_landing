import csv
import logging
import os
from logging import Formatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('debug.log.example', mode='a', encoding='UTF-8')
logger.addHandler(handler)
formatter = Formatter(
    '{asctime}, {levelname}, {message}', style='{'
)
handler.setFormatter(formatter)


class FailedRequestApi(Exception):
    """Исключение для неудачного запроса."""
    pass


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def save_items_to_csv(items, folder_name, category):
    csv_path = os.path.join(folder_name, f"{category}.csv")

    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([items['title'], items['buyUrl'],
                         items['price']])
