import logging
from typing import Optional
from queue import Queue
from logs.logging_config import setup_logging
from parsers.extract_number import extract_number
from parsers.selenium_object import get_bs4_with_selenium
from threading import Thread

setup_logging()
logger = logging.getLogger(__name__)


def parser_page(url: str, page_num: int, result_queue: Queue) -> None:
    """
    Парсит страницу и добавляет результат в очередь.

    Параметры:
        url (str): URL страницы для загрузки и парсинга,
        page_num(str): номер страницы который парсим (переменная для логов).
    Возвращает:
        None

    Исключения:
        WebDriverException: Если основной контейнер контента не найден.
        TimeoutException: Если спиннер не исчезает в течение заданного времени.
        Exception: При других критических ошибках во время загрузки или парсинга.
    """
    res = {
        "sum_price_product": 0,
        "total_products": 0,
    }

    logger.debug(f"Обрабатывается страница {page_num}")

    bs4object = get_bs4_with_selenium(url)

    # Поиск товаров
    products = bs4object.find_all("div", class_="indexGoods__item")
    if not products:
        logger.warning("Товары не найдены на странице")

    logger.info(f"Найдено {len(products)} товаров на странице {page_num}")

    # Обработка товаров
    for product in products:
        price_element = product.find("span", class_="price")
        if price_element:
            # Получение очищенного числа от возможных символов
            price = extract_number(str(price_element))
            if price:
                res["sum_price_product"] += price
                res["total_products"] += 1

    result_queue.put(res)  # Отправляем результат в очередь


def get_count_page() -> Optional[int]:
    """
    Определяет общее количество страниц с товарами для заданной категории.

    Возвращает:
        int: Количество страниц с товарами
        None: Если не удалось определить количество страниц
    """
    url = "https://www.onlinetrade.ru/catalogue/smartfony-c13/?presets=0&preset_id=0&producer%5B0%5D=XIAOMI&price1=5990&price2=156999&diagonal1=6.36&diagonal2=6.88&volume_akumm1=4780&volume_akumm2=5500&advanced_search=1&rating_active=0&special_active=1&selling_active=1&producer_active=1&price_active=0&os_active=1&platform_active=1&volume_mem_active=1&ram_active=1&diagonal_active=1&display_razr_active=0&chastota_obnovleniya_active=1&fotokamera_osnovnaya_active=1&front_camera_active=1&processor_active=1&phones_type_active=1&slot_dlya_karti_pamyati_active=1&fbz_active=1&besprovod_zaryad_active=1&radio_active=1&nfc_active=1&5g_active=1&kov_sim_active=1&stepen_zashchiti_active=0&color_active=1&volume_akumm_active=1"
    try:
        logger.debug("Получение данных с основной страницы")
        soup = get_bs4_with_selenium(url)

        if not soup:
            logger.error("Не удалось получить содержимое страницы")
            return None

        # Получение строки с данными
        logger.debug("Поиск элемента пагинации")
        paginator_count = soup.find("div", class_="paginator__count").get_text(strip=True)

        if not paginator_count:
            logger.warning("Элемент пагинации не найден")
            return None

        # Обработка текста с количеством товаров
        info_text = paginator_count.replace("Показано:", "").replace(" из", "").strip().split(" ")
        logger.debug(f"Получен текст пагинации: {info_text}")

        # Получение общего кол-ва товаров и кол-ва товаров на одной странице
        total_products = int(info_text[1])
        products_in_page = int(info_text[0][2:])

        # Расчет количества страниц
        count_pages = (total_products + products_in_page - 1) // products_in_page  # Округление вверх
        logger.info(f"Успешно определено, что кол-во страниц с товарами = {count_pages}")
        return count_pages

    except AttributeError as exp:
        logger.error(f"Ошибка парсинга: {str(exp)}")
    except ValueError as exp:
        logger.error(f"Ошибка преобразования данных: {str(exp)}")
    except Exception as exp:
        logger.error(f"Непредвиденная ошибка: {str(exp)}", exc_info=True)


def parser_online_trade():
    """
    Парсинг сайта onlinetrade.ru для сбора статистики по смартфонам Xiaomi.
    Возвращает словарь с общей суммой цен и количеством товаров.
    """

    total = {"total_price": 0, "total_products": 0}
    result_queue = Queue()  # Создаем очередь для результатов

    # Количество страниц с товарами
    pages_count = get_count_page()
    if not pages_count:
        logger.error("Не удалось определить количество страниц.")
        return total  # Возвращаем пустой результат

    logger.info("Запуск парсера для onlinetrade.ru")
    threads = []

    for page_num in range(pages_count):
        try:
            url = (
                f"https://www.onlinetrade.ru/catalogue/smartfony-c13/?presets=0&preset_id=0&"
                f"producer%5B0%5D=XIAOMI&price1=5990&price2=156999&diagonal1=6.36&diagonal2=6.88&"
                f"volume_akumm1=4780&volume_akumm2=5500&advanced_search=1&rating_active=0&"
                f"special_active=1&selling_active=1&producer_active=1&price_active=0&os_active=1&"
                f"platform_active=1&volume_mem_active=1&ram_active=1&diagonal_active=1&"
                f"display_razr_active=0&chastota_obnovleniya_active=1&fotokamera_osnovnaya_active=1&"
                f"front_camera_active=1&processor_active=1&phones_type_active=1&slot_dlya_karti_pamyati_active=1&"
                f"fbz_active=1&besprovod_zaryad_active=1&radio_active=1&nfc_active=1&5g_active=1&"
                f"kov_sim_active=1&stepen_zashchiti_active=0&color_active=1&volume_akumm_active=1&page={page_num}"
            )

            thread = Thread(target=parser_page, args=(url, page_num, result_queue))
            threads.append(thread)
            thread.start()  # Запускаем поток

        except Exception as e:
            logger.error(f"Ошибка при создании потока для страницы {page_num}: {str(e)}")

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

    # Сбор результатов из очереди
    while not result_queue.empty():
        result = result_queue.get()
        total["total_price"] += result["sum_price_product"]
        total["total_products"] += result["total_products"]

    logger.info("Итоговые результаты: %s", total)
    return total
