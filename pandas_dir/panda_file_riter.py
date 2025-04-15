import os
import pandas as pd
import logging
from typing import Optional

from logs.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_data_file(filename: str) -> Optional[pd.DataFrame]:
    """
    Загружает и валидирует данные из Excel-файла в директории downloads.

    Args:
        filename (str): Имя файла для загрузки (с расширением)

    Returns:
        pd.DataFrame: DataFrame с данными или None при критической ошибке

    Raises:
        FileNotFoundError: Если файл не существует
        KeyError: Если отсутствуют обязательные колонки
        ValueError: Если файл не является валидным Excel-файлом
    """
    try:
        # Формирование пути к директории
        downloads_dir = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
        logger.debug("Старт обработки файла: %s", filename)

        # Создание директории при необходимости
        os.makedirs(downloads_dir, exist_ok=True)
        logger.info("Директория проверена: %s", downloads_dir)

        # Проверка существования файла
        file_path = os.path.join(downloads_dir, filename)
        if not os.path.isfile(file_path):
            logger.error("Файл не найден по пути: %s", file_path)
            raise FileNotFoundError(f"Файл {filename} не найден в папке downloads")

        # Чтение файла
        logger.info("Начало чтения файла: %s", filename)
        df = pd.read_excel(file_path)
        logger.debug("Успешно прочитано строк: %d", len(df))

        # Проверка структуры данных
        required_columns = {'title', 'url', 'xpath'}
        logger.debug("Проверка обязательных колонок")

        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            logger.critical("Отсутствуют колонки: %s", missing)
            raise KeyError(f"Отсутствуют обязательные колонки: {missing}")

        logger.info("Файл успешно загружен и проверен")
        return df

    except FileNotFoundError as fnf_error:
        logger.error("Ошибка файла: %s", str(fnf_error))
        raise
    except pd.errors.EmptyDataError:
        logger.critical("Файл пуст или поврежден: %s", filename)
        raise ValueError("Файл не содержит данных")
    except Exception as e:
        logger.critical("Непредвиденная ошибка: %s", str(e), exc_info=True)
        raise
