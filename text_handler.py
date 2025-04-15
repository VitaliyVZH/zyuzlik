import pandas as pd
import logging
from logs.logging_config import setup_logging
from parsers.extract_number import extract_number

logger = logging.getLogger(__name__)
setup_logging()


def get_text(data: pd.DataFrame) -> str:
    """
    Форматирует данные из DataFrame в читаемый текстовый формат.

    Args:
        data (pd.DataFrame): DataFrame с обязательными колонками:
            - title: Название товара
            - url: Ссылка на товар
            - xpath: HTML-контент с ценой

    Returns:
        str: Отформатированная строка с данными или сообщение об отсутствии данных

    Raises:
        KeyError: Если отсутствуют необходимые колонки в DataFrame
    """
    logger.info("Начало обработки данных")

    try:
        # Проверка наличия обязательных колонок
        required_columns = {'title', 'url', 'xpath'}
        if not required_columns.issubset(data.columns):
            missing = required_columns - set(data.columns)
            logger.critical(f"Отсутствуют колонки: {missing}")
            raise KeyError(f"Отсутствуют обязательные колонки: {missing}")

        text = []
        processed_count = 0
        error_count = 0

        for index, row in data.iterrows():
            try:
                logger.debug(f"Обработка строки {index + 1}")

                # Извлечение и проверка данных
                title = str(row['title']).strip()
                url = str(row['url']).strip()
                price_content = extract_number(str(row['xpath']))

                # Валидация полей
                if not all([title, url, price_content]):
                    logger.warning(f"Пропуск строки {index + 1} - отсутствуют данные")
                    error_count += 1
                    continue

                # Форматирование записи
                text.append(
                    f"{index + 1}. {title}\n"
                    f"Ссылка: {url}\n"
                    f"Цена: {price_content}\n"
                )
                processed_count += 1

            except Exception as e:
                logger.error(f"Ошибка обработки строки {index + 1}: {str(e)}")
                error_count += 1
                continue

        logger.info(f"Обработка завершена. Успешно: {processed_count}, Ошибок: {error_count}")

        if text:
            return '\n'.join(text)
        logger.warning("Нет данных для отображения")
        return "Данные не найдены"

    except Exception as e:
        logger.critical(f"Критическая ошибка обработки данных: {str(e)}", exc_info=True)
        raise
