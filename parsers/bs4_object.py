"""Модуль реализует получение объекта BeautifulSoup из указанного сайта."""

import requests
import logging
from bs4 import BeautifulSoup
from logs.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


def get_bs4(url: str, parser: str = "lxml", raise_for_status: bool = True, **kwargs):
    """
    Получает объект BeautifulSoup из указанного URL

    Аргументы:
        url: Целевая веб-страница
        parser: Парсер для BeautifulSoup (по умолчанию: lxml)
        raise_for_status: Вызывать исключение при статусах кроме 200
        **kwargs: Дополнительные аргументы для requests.get()

    Возвращает:
        Объект BeautifulSoup

    Вызывает:
        RuntimeError: Ошибки при выполнении запроса или парсинга
    """
    try:
        # Логирование начала запроса
        logger.info(f"Начало обработки URL: {url}")
        logger.debug(f"Параметры запроса: {kwargs}")

        # Выполняем HTTP-запрос
        response = requests.get(url, allow_redirects=True, **kwargs)
        logger.info(f"Получен ответ. Статус код: {response.status_code}")

        # Проверяем статус ответа при необходимости
        if raise_for_status:
            response.raise_for_status()
            logger.debug("Проверка статуса выполнена успешно")

        # Проверяем поддерживаемые парсеры
        if parser not in {"lxml", "html.parser", "html5lib"}:
            error_msg = f"Неподдерживаемый парсер: {parser}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Парсинг содержимого
        logger.info(f"Начало парсинга с использованием {parser}")
        soup_object = BeautifulSoup(response.content, "lxml")
        logger.debug("Парсинг завершен успешно")
        print(soup_object)
        return soup_object

    except requests.exceptions.RequestException as re:
        error_msg = f"Сетевая ошибка: {str(re)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from re

    except Exception as exp:
        error_msg = f"Непредвиденная ошибка: {str(exp)}"
        logger.critical(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from exp


