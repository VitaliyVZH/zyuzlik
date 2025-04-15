from bs4 import BeautifulSoup
import logging
from typing import Optional, Union
from logs.logging_config import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


def clean_price_string(dirty_price_str: str) -> Optional[int]:
    """Очищает строку с ценой от нецифровых символов и преобразует в целое число."""
    try:
        logger.debug(f"Начальная очистка цены: '{dirty_price_str}'")
        price_str = "".join([symbol for symbol in dirty_price_str if symbol.isdigit()])

        if not price_str:
            logger.warning(f"Не найдено цифр в строке: '{dirty_price_str}'")
            return None

        logger.debug(f"Очищенная числовая строка: '{price_str}'")
        return int(price_str)

    except Exception as e:
        logger.error(f"Ошибка при обработке цены '{dirty_price_str}': {str(e)}", exc_info=True)
        return None


def extract_number(html: str) -> Optional[int]:
    """
    Извлекает и очищает числовое значение цены из HTML-строки.

    Args:
        html (str): HTML-строка содержащая цену. По умолчанию: "11 990 ₽"

    Returns:
        Optional[int]: Целочисленное значение цены или None при ошибке

    Raises:
        AttributeError: Если не удалось извлечь числовое значение
        Exception: При других ошибках парсинга
    """
    try:
        logger.info(f"Начало обработки HTML-контента. Длина: {len(html)} символов")
        logger.debug(f"Полученный HTML фрагмент: {html[:100]}...")  # Ограничиваем длину лога

        soup = BeautifulSoup(html, "lxml")
        dirty_price_string = soup.get_text(strip=True)
        logger.debug(f"Текст после BeautifulSoup: '{dirty_price_string}'")

        price = clean_price_string(dirty_price_string)

        if price is None:
            logger.error("Не удалось извлечь цену из текста: '%s'", dirty_price_string)
            raise AttributeError("Цена не найдена в переданном HTML")

        logger.info(f"Успешно извлечена цена: {price}")
        return price

    except AttributeError as ae:
        logger.error(f"Ошибка атрибута: {str(ae)}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Критическая ошибка при обработке HTML: {str(e)}", exc_info=True)
        return None
