import logging
import pandas
from database.db_manager import Database
from logs.logging_config import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


def insert_data_bd(data: pandas) -> None:
    """Вставляет данные из DataFrame в таблицу zyuzlik."""
    try:
        # Проверка наличия необходимых колонок в данных
        required_columns = {'title', 'url', 'xpath'}
        if not required_columns.issubset(data.columns):
            missing = required_columns - set(data.columns)
            logger.error(f"Отсутствуют обязательные колонки: {missing}")
            raise ValueError(f"Отсутствуют колонки: {missing}")

        with Database() as db:
            with db.connection:
                cursor = db.connection.cursor()
                # Конвертация DataFrame в список кортежей для пакетной вставки
                data_tuples = [
                    (row['title'], row['url'], row['xpath'])
                    for _, row in data.iterrows()
                ]
                # Пакетная вставка данных
                cursor.executemany('''
                    INSERT INTO zyuzlik (title, url, xpath)
                    VALUES (?, ?, ?)
                ''', data_tuples)
                inserted_rows = cursor.rowcount
                logger.info(f"Успешно импортировано {inserted_rows} записей")
    except Exception as e:
        logger.error(f"Ошибка импорта данных: {str(e)}")
        raise
